# OpenADR 3 Virtual Top Node (VTN) Reference Implementation

## Requirements
Python 3.10 (newer versions may break gevent/connexion dependencies)

## Configuration

The VTN is configured via `config.yaml` in the project root. All settings can also be
overridden by environment variables. If `config.yaml` is not present or PyYAML is not
installed, the server falls back to environment variables and built-in defaults.

To use a different config file path, set the `VTN_CONFIG` environment variable:
```bash
VTN_CONFIG=/path/to/my-config.yaml python -m swagger_server
```

Key configuration sections:

| Section | Description |
|---------|-------------|
| `server` | Bind address, port, log level |
| `storage` | Backend (`IN_MEMORY` or `IN_FILE`) and file path |
| `auth` | Provider (`basic` or `oidc`) and client credentials |
| `notifications` | Enabled bindings (`WEBHOOK`, `MQTT`) |
| `mqtt` | Broker connection, auth method, topic base paths |
| `mdns` | Optional mDNS service advertisement |

See `config.yaml` for the full list of settings with comments.

### MQTT Support

OpenADR >= 3.1.0 defines optional support for notifications via pub-sub messaging.
See [Messaging and MQTT Support](docs/MESSAGING.md) for details.

To use MQTT, an MQTT broker must be running. [Mosquitto](https://mosquitto.org) is
recommended for development and testing.

To disable MQTT, remove `MQTT` from `notifications.bindings` in `config.yaml`:
```yaml
notifications:
  bindings:
    - WEBHOOK
```

### mDNS Service Advertisement

The VTN can optionally advertise itself via mDNS (Bonjour/Avahi) so that local
clients can discover it without hardcoding URLs. The service is advertised as
`_openadr3._tcp.local.` with the VTN's port and base path.

Enable in `config.yaml`:
```yaml
mdns:
  enabled: true
  service_name: OpenADR3 VTN
```

Requires the `zeroconf` Python package (included in `requirements.txt`).
Disabled by default — zero impact when off.

## Running locally with Python

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install 'setuptools<81'
pip install -r requirements.txt
python -m swagger_server
```

### Using the startup scripts

Shell scripts are provided in `bin/` for managing the VTN and supporting services
via [tmux](https://github.com/tmux/tmux):

```bash
bin/vtn-start.sh              # Start VTN-RI in a tmux session
bin/vtn-stop.sh               # Stop VTN-RI
bin/vtn-status.sh             # Check if running + HTTP health
bin/stack-start.sh             # Start Mosquitto + VTN-RI
bin/stack-start.sh --with-callback  # Also start the test callback service
bin/stack-stop.sh              # Stop VTN-RI + callback service
```

`vtn-start.sh` handles venv creation, dependency installation, and waits for
the HTTP server to be ready. It accepts an optional config file path argument:
```bash
bin/vtn-start.sh my-custom-config.yaml
```

#### MQTT broker management

`stack-start.sh` auto-detects the platform and uses `brew services` (macOS) or
`systemctl` (Linux) to start Mosquitto. To use a different broker or command:

```bash
# Custom start command
MQTT_START_CMD="docker start mosquitto" bin/stack-start.sh

# Skip broker management (e.g. using a remote broker)
MQTT_START_CMD=none bin/stack-start.sh

# Or skip MQTT entirely
bin/stack-start.sh --no-mqtt
```
## Building and Running with Docker

To run the server in a Docker container, execute the following from the root directory:

```bash
# building the image
docker build -t swagger_server .

# starting up a container
docker run -p 8080:8080 swagger_server
```

The above assumes that you are building a Docker image for the same architecture as the host you are building them on.
If building a Docker image for another architecture, the `--platform` flag must be specified.
And to build a multi-platform image, list each architecture, e.g. `--platform linux/arm64,linux/amd64`
[This blog post from David Herron](https://techsparx.com/software-development/docker/tutorials/multi-stage-multi-platform.html) provides further explanation and insight.

To run both the server and the Mosquitto MQTT broker in containers:

```bash
docker compose up
```

This runs both Docker containers, as specifed in `compose.yaml`, and the Mosquitto broker's configuration is `cfg/mosquitto/config/mosquitto.conf`

Both VTN's port `8080` and the Mosquitto MQTT broker's port `1883` are mapped and exposed to those same ports on the Docker host.

Note the presence of Dockerfile-lambda. This is used by a CI/CD pipeline to create a
Docker image which is pushed to a cloud environment to support the online OADR3 Test Tool.
The details of the CI/CD pipeline are described elsewhere.

## Running locally with AWS SAM CLI

`Dockerfile-lambda` can also be used to run the Lambda function locally via the
[AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html),
which emulates the API Gateway and Lambda runtime on your machine without
deploying anything to AWS.

```bash
./run-sam-local.sh
```

The script builds the Docker image and starts a local HTTP API on
`http://localhost:8080`. See [docs/running-locally-sam.md](docs/running-locally-sam.md)
for full prerequisites, configuration options, and example requests.

## Interacting with the running VTN

The VTN listens for requests on

	http://localhost:8080/openadr3/3.1.0

Currently, the VTN only uses HTTP, not HTTPS, and
uses Basic auth with base64-encoded `client_id:secret` tokens.
The default clients are configured in `config.yaml`:

| Client | client_id:secret | Role | Base64 Token |
|--------|-----------------|------|-------------|
| BL | `bl_client:1001` | Business Logic | `YmxfY2xpZW50OjEwMDE=` |
| VEN | `ven_client:999` | VEN | `dmVuX2NsaWVudDo5OTk=` |
| VEN2 | `ven_client2:9999` | VEN | `dmVuX2NsaWVudDI6OTk5OQ==` |

A simple way to verify the VTN is running and accessible:
```bash
curl -H "Authorization: Bearer YmxfY2xpZW50OjEwMDE=" http://localhost:8080/openadr3/3.1.0/programs
```
The expected result:
```bash
[]
```

In typical scenarios, the VTN will need to be "loaded" with OpenADR 3 objects (programs, events, etc) via
the Business Logic (BL) client endpoints (using the `bl_token` above),
subsequently VEN client endpoints/requests may be invoked to retrieve these objecs.

The [openadr3-test-tool](https://github.com/oadr3-org/openadr3-test-tool) repo contains a number of useful test scripts.

### Integration Tests

**NOTE: This feature is currently not working, see Issue [#63](https://github.com/oadr3-org/openadr3-vtn-reference-implementation/issues/63), PRs to fix this are welcome!**

```
pip install tox
tox
```

## Viewing the OpenAPI specs from the running VTN

**NOTE: This feature is currently not working, see Issue [#81](https://github.com/oadr3-org/openadr3-vtn-reference-implementation/issues/81), PRs to fix this are welcome!**

Open your browser to: `http://localhost:8080/openadr3/3.0.1/ui/`

Before interacting with API, select the `Authorize` button at top Right of API operations.
(Just above Auth GET section).

In dialog, type one of two pre-defined tokens, "ven_token" or "bl_token", into BearerAuth value text box.
Select `Authorize`, and `Close`.

## Implementation Notes

The Reference Implementation is auto-generated by Swaggerhub.
We paste the `openadr3.yaml` file into the edit pane at https://app.swaggerhub.com/apis/openadr3/OpenADR-3.0.0/3.1.0,
and select 'Export -> Server Stub -> python-flask' to download a file named 'python-flask-server-generated.zip'.
Decompressing this file results in a folder containing the RI stub.

The RI stub contains a fully executable server, with all endpoints and endpoint handlers present, e.g. a POST to `/events` will invoke the `create_event()` method in `./swagger_server/controllers/events_controller.py`

We add logic to the modules in the `swagger_server/controllers folder`. For example, we add code to `events_controller.create_event()` to replace the stub statement

```
return 'do some magic!'
```

with code to instantiate an event object, save it, and return a representation of the object.

### OpenAPI Specification Workflow

The OpenADR3 [specification](https://github.com/oadr3-org/specification) is maintained as a separate project on GitHub,
and the OpenAPI YAML definition is in `./{version}/openadr3.yaml`, for example: `./3.1.0/openadr3.yaml`

In order to maintain synchronization between the RI and the specification ,
we create issues in the RI project associated with issues in the specification.
When the specification is updated, we update the RI using the following process:

- Copy the latest version of `openadr3.yaml` into the edit pane of [Swaggerhub](https://app.swaggerhub.com/) and autogenerate a new server stub, as described above.
- Copy the stub `swagger_server/swagger/swagger.yaml` into the same folder of the RI, overwriting the existing.
- Where there are changes to the schemas, copy the new or modified files in `swagger_server/models` from the stub to the same folder in the RI.
- Where there are new endpoints, copy new modules to `swagger_server/controllers` and add logic.
- Where there are modified endpoints or operations, one must merge the contents of the stub controllers to the existing RI controllers. This will likely take the form of simply adding new material to the existing files.

There may occasionally be changes to `openadr3.yaml` that affect components of the RI beyond the `swagger_server/[swagger, models, components]` folders.
These can be found by diffing the stub and RI folders and identifying affected files and performing the appropriate modifications to the RI.

Updates to the RI will often require updates to VTN tests, maintained in the [openadr3-test-tool](https://github.com/oadr3-org/openadr3-test-tool) project.

In the future, this workflow may be improved, for example by utilizing a command line tool to generate the server stub instead of relying on the Swaggerhub website.
