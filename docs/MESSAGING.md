# Messaging and MQTT Support in OpenADR >= 3.1.0

## Overview

OpenADR 3.1.0 added (optional) support for notifications via publish-subscribing messaging,
and the design is intended to support multiple messaging protocols,
each protocol defined by a binding.

Initially, a single binding is specified, MQTT.

The OpenADR3 REST API was extended to include new endpoints to enable clients to query the VTN
to ascertain the VTN's support for messaging and the MQTT messaging binding.

## VTN Reference Implementation Configuration

The VTN-RI supports configuation options via the file `config.py`

The VTN-RI includes support for messaging and the MQTT messsaging binding,
both of which are enabled and configured in `config.py` as described subsequently.

## Messaging Endpoint

A VTN **MAY** support messaging, but **MUST** support the new `GET /brokers` endpoint.

A VTN that doesn't support the messaging option **MUST** respond to `GET /brokers` request
with an empty `BrokersResponse` object, which is simply an empty object `{}`

### Example of disabled messaging support in the VTN-RI:

To disable messaging support, set `MESSAGING_BINDINGS = []`

```
% curl -H "Content-type: application/json" \
       -H "Authorization: Bearer ven_token" \
       http://localhost:8080/openadr3/3.1.0/brokers

{}
```

Again, the empty object response `{}` indicates that no messaging bindings are supported by this VTN.

### Example of enabled MQTT messaging support in the VTN-RI:

To enable the MQTT binding, set `MESSAGING_BINDINGS = ['MQTT']`

```
% curl -H "Content-type: application/json" \
       -H "Authorization: Bearer ven_token" \
	   http://localhost:8080/openadr3/3.1.0/brokers

{
  "MQTT": {
    "auth": "ANONYMOUS",
    "connectionURI": "mqtt://127.0.0.1",
    "serialization": "JSON"
  }
}
```

This response indicates the VTN supports the MQTT messaging binding, and provides connection, authorization, and serialization details for the MQTT binding.

## MQTT Messaging Binding Endpoints

### MQTT binding endpoints, HTTP `GET` method:

The following OpenADR3 REST API endpoints are defined for the MQTT messaging binding:

- `/brokers/mqtt/topics/programs`
- `/brokers/mqtt/topics/programs/{programID}`
- `/brokers/mqtt/topics/programs/{programID}/events`
- `/brokers/mqtt/topics/programs/{programID}/reports`
- `/brokers/mqtt/topics/programs/{programID}/subscriptions`
- `/brokers/mqtt/topics/vens`
- `/brokers/mqtt/topics/vens/{venID}/resources`
- `/brokers/mqtt/topics/vens/{venID}/events`
- `/brokers/mqtt/topics/vens/{venID}/programs`

### MQTT binding endpoint response when messaging/MQTT not supported by VTN:

When messaging/MQTT is not supported by the VTN, a client request to any of these endpoints **MUST** respond with an HTTP status of `404`:

```
% curl -H "Content-type: application/json" \
       -H "Authorization: Bearer ven_token" \
	   http://localhost:8080/openadr3/3.1.0/brokers/mqtt/topics/programs

{
  "status": 404,
  "title": "MQTT binding not enabled",
  "type": "about:blank"
}
```

### Example MQTT endpoint response when messaging/MQTT enabled:

When MQTT messaging support is enabled in the VTN-RI, an example request/response:

```
% curl -H "Content-type: application/json" \
       -H "Authorization: Bearer ven_token" \
	   http://localhost:8080/openadr3/3.1.0/brokers/mqtt/topics/programs

{
  "binding": "MQTT",
  "objectType": "PROGRAM",
  "topics": {
    "ALL": "programs/+",
    "CREATE": "programs/create",
    "DELETE": "programs/delete",
    "UPDATE": "programs/update"
  }
}
```

This response provides the topic paths a client may subscribe to in order to receive notifications of operations on the requested/indicated `object_type`.

### VEN-Targeted Topics

When a `PROGRAM` or `EVENT` has `targets` that match a VEN's targets, notifications are also published to VEN-specific topics. This allows VEN clients to subscribe only to topics relevant to them.

For example, if a VEN with `venID=5` is targeted by a program, the notification is published to both the general `programs/create` topic and the VEN-targeted `programs/vens/5/create` topic.

The VEN-targeted topic endpoints are:

- `/brokers/mqtt/topics/vens/{venID}/events` — events targeted at a specific VEN
- `/brokers/mqtt/topics/vens/{venID}/programs` — programs targeted at a specific VEN

An example of a failing request for topics:

```
% curl -H "Content-type: application/json" \
       -H "Authorization: Bearer ven_token" \
	   http://localhost:8080/openadr3/3.1.0/brokers/mqtt/topics/programs/1

{
  "status": 404,
  "title": "programID=1 not found",
  "type": "about:blank"
}
```

This request failed because no `PROGRAM` with `programID=1` was found on the VTN.

### Example of notifications resulting from `PROGRAM` creation

A BL client creates a `PROGRAM`:

```
% curl -X POST \
       -H "Content-type: application/json" \
	   -H "Authorization: Bearer bl_token"  \
	   -d @program.json \
	   http://localhost:8080/openadr3/3.1.0/programs

{
  "createdDateTime": "09:21:33",
  "id": "0",
  "objectType": "PROGRAM",
  "programName": "minimalProgram"
}
```

The side-effects of the `PROGRAM` `CREATE` are the `Notification` object is published to the following topics on the MQTT broker:

- `programs/create`
- `programs/0/create`

And in this example, the notification object published:

```
{
  "object_type": "PROGRAM",
  "operation": "CREATE",
  "object": {
    "program_name": "minimalProgram",
    "program_long_name": null,
    "retailer_name": null,
    "retailer_long_name": null,
    "program_type": null,
    "country": null,
    "principal_subdivision": null,
    "time_zone_offset": null,
    "interval_period": null,
    "program_descriptions": null,
    "binding_events": null,
    "local_price": null,
    "payload_descriptors": null,
    "targets": null,
    "id": "0",
    "created_date_time": "09:21:33",
    "modification_date_time": null,
    "object_type": "PROGRAM"
  },
  "targets": null
}
```
