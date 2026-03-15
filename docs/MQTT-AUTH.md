# MQTT Broker Authentication

By default, the VTN-RI connects to the MQTT broker with anonymous access — any
client can connect and subscribe to any topic. For production or multi-tenant
deployments, authenticated access with per-VEN topic-level ACLs is supported via
Mosquitto's [Dynamic Security Plugin](https://mosquitto.org/documentation/dynamic-security/).

This is Phase 1 of MQTT security: username/password authentication with
dynsec-managed ACLs. OAuth2 bearer token auth and TLS are planned for future
phases.

## Overview

When dynsec is enabled:

1. The VTN connects to the broker as an admin user with publish access to all
   topics and the dynsec control topic.
2. When a VEN is created via the REST API, the VTN provisions a broker account
   (`ven-{venID}`) with topic ACLs scoped to that VEN's resources.
3. When a VEN calls `GET /notifiers`, its per-VEN MQTT credentials are returned
   in the binding response.
4. When a VEN is deleted, its broker account is removed.

On VTN restart, MQTT passwords are regenerated for all existing VENs (credentials
are held in-memory only).

## Setup

### 1. Configure broker credentials

In `config.yaml`, set the broker auth method and admin credentials:

```yaml
mqtt:
  broker:
    auth: OAUTH2_BEARER_TOKEN
    username: vtn-admin
    password: your-secure-password
```

These can also be set via environment variables `MQTT_BROKER_USERNAME` and
`MQTT_BROKER_PASSWORD`.

### 2. Bootstrap the broker

Run the bootstrap script to generate the Mosquitto config and initial
`dynamic-security.json`:

```bash
bin/bootstrap-mosquitto-dynsec.sh
```

This creates two files in `cfg/mosquitto/dynsec/`:

- **`mosquitto-dynsec.conf`** — Mosquitto config that loads the dynsec plugin,
  sets the listener port, and disables anonymous access.
- **`dynamic-security.json`** — Initial dynsec state with the VTN admin user
  and three static roles.

The script reads all settings from `config.yaml` (single source of truth). Pass
a custom config path as the first argument or via `VTN_CONFIG`:

```bash
bin/bootstrap-mosquitto-dynsec.sh my-config.yaml
```

### 3. Start Mosquitto

```bash
mosquitto -c cfg/mosquitto/dynsec/mosquitto-dynsec.conf
```

### 4. Start the VTN

```bash
python -m swagger_server
```

The VTN will connect as the admin user, initialize the `DynsecManager`, and
regenerate MQTT credentials for any VENs already in the object store.

## ACL Design

### Static roles (created at bootstrap)

**`vtn-publisher`** — assigned to the VTN admin user:
- `publishClientSend` on `#` (publish to all notification topics)
- `publishClientSend` on `$CONTROL/dynamic-security/v1` (dynsec commands)
- `subscribePattern` on `$CONTROL/dynamic-security/v1/response`

**`bl-subscriber`** — for BL (Business Logic) clients:
- `subscribePattern` on `programs/#`, `events/#`, `reports/#`,
  `subscriptions/#`, `vens/#`, `resources/#`

**`ven-base`** — assigned to all VEN clients:
- `subscribePattern` on `programs/+` (untargeted program notifications)
- `subscribePattern` on `events/+` (untargeted events)
- `subscribePattern` on `reports/+`
- `subscribePattern` on `subscriptions/+`

### Per-VEN roles (created at runtime)

When a VEN is created, a role `ven-{venID}` is provisioned with:
- `subscribePattern` on `vens/{venID}/#`
- `subscribePattern` on `resources/vens/{venID}/#`
- `subscribePattern` on `programs/vens/{venID}/#` (targeted programs)
- `subscribePattern` on `events/vens/{venID}/#` (targeted events)
- `subscribePattern` on `events/programs/+/#` (per-program events)

### Default access

All access is denied by default (`publishClientSend: false`,
`subscribe: false`), except `publishClientReceive: true` and
`unsubscribe: true`.

## Credential Delivery

A VEN discovers its MQTT credentials by calling `GET /notifiers`. When dynsec is
active, the response includes the VEN's broker username and password in the MQTT
binding:

```json
{
  "webhook": true,
  "mqtt": {
    "uris": ["mqtt://127.0.0.1"],
    "serialization": "JSON",
    "authentication": {
      "method": "OAUTH2_BEARER_TOKEN",
      "username": "ven-abc123",
      "password": "randomly-generated-token"
    }
  }
}
```

The `password` field is only present when dynsec is active. With anonymous auth,
the binding omits credentials.

## VEN MQTT Username Convention

VEN broker usernames follow the pattern `ven-{venID}`. This is:
- Unique per VEN
- Maps directly to topic paths for ACL scoping
- Easy to identify in broker logs

## Credential Lifecycle

| Event | Action |
|-------|--------|
| VEN created (REST API) | Broker account + per-VEN role provisioned |
| VEN calls `GET /notifiers` | Credentials returned in binding |
| VEN deleted (REST API) | Broker account + role deleted |
| VTN restart | Fresh passwords generated for all existing VENs |

Credentials are stored in-memory only (`globals.VEN_MQTT_CREDENTIALS`). On VTN
restart, all VEN passwords are regenerated via `setClientPassword`. A VEN must
call `GET /notifiers` after a VTN restart to obtain its new credentials.

## Files

| File | Purpose |
|------|---------|
| `bin/bootstrap-mosquitto-dynsec.sh` | Bootstrap script |
| `cfg/mosquitto/dynsec/` | Generated mosquitto config + dynsec JSON |
| `config.yaml` | `mqtt.broker.username`, `mqtt.broker.password` |
| `config.py` | `MQTT_BROKER_USERNAME`, `MQTT_BROKER_PASSWORD` |
| `swagger_server/dynsec.py` | `DynsecManager` class |
| `swagger_server/globals.py` | `DYNSEC`, `VEN_MQTT_CREDENTIALS` |
| `swagger_server/notifiers.py` | Dynsec hooks in `ven_tracker()` |
| `swagger_server/controllers/notifiers_controller.py` | Caller-aware `/notifiers` |
