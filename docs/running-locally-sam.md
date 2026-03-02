# Running the VTN Lambda locally with AWS SAM CLI

This guide describes how to build and run the OpenADR3 VTN Lambda function on
your local machine using the AWS SAM CLI.

## Prerequisites

### 1. Docker

SAM runs the Lambda function inside a Docker container that matches the AWS
Lambda runtime. Docker must be installed and the Docker daemon must be running
before you start.

- Download: https://docs.docker.com/get-docker/
- Verify: `docker info`

### 2. AWS SAM CLI

The script uses `sam.cmd` (the Windows wrapper for SAM CLI).

- Download: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
- Verify: `sam.cmd --version`

### 3. Git Bash (or any bash-compatible shell)

The script `run-sam-local.sh` uses bash syntax. On Windows use Git Bash,
WSL, or any MSYS2-based terminal.

---

## How it works

```
HTTP request (curl / browser / Postman)
        |
        | :8080
        v
  SAM CLI  (sam local start-api)
  - translates HTTP → API Gateway v2 event
  - invokes handler inside Docker container
        |
        v
  Dockerfile-lambda  (public.ecr.aws/lambda/python:3.13)
  - lambda.handler
  - awsgi → Flask / Connexion app
```

Key files involved:

| File | Role |
|---|---|
| `Dockerfile-lambda` | Lambda container image definition |
| `template.yaml` | SAM template — wires the image to an HTTP API |
| `lambda.py` | Lambda handler entry point |
| `run-sam-local.sh` | Build + start script |

---

## Running

From the project root directory, execute:

```bash
./run-sam-local.sh
```

The script performs two steps:

1. **`sam.cmd build`** — builds the Docker image from `Dockerfile-lambda` and
   packages it for local use.
2. **`sam.cmd local start-api --port 8080 --warm-containers EAGER`** — starts a
   local HTTP server that routes incoming requests to the Lambda handler.
   `EAGER` mode keeps the container warm so subsequent requests are fast.

The API is ready when you see output similar to:

```
Mounting VtnFunction at http://127.0.0.1:8080/{proxy+} [DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT]
You can now browse to the above endpoints to invoke your functions.
```

Press **Ctrl+C** to stop.

---

## Sending requests

The base path of the API is `/openadr3/3.1.0`. Basic auth credentials are
defined in `config.py`.

| Credential | Value |
|---|---|
| VEN client ID | `ven_client` |
| VEN secret | `999` |
| BL client ID | `bl_client` |
| BL secret | `1001` |

### Examples

```bash
# List programs
curl http://localhost:8080/openadr3/3.1.0/programs

# Create a program (with basic auth)
curl -X POST http://localhost:8080/openadr3/3.1.0/programs \
  -u ven_client:999 \
  -H "Content-Type: application/json" \
  -d '{
    "programName": "test",
    "programLongName": "Test Program",
    "country": "US",
    "principalSubdivision": "CA",
    "timeZoneOffset": "PT0S",
    "programType": "PRICING"
  }'

# List events
curl http://localhost:8080/openadr3/3.1.0/events

# List VENs
curl http://localhost:8080/openadr3/3.1.0/vens
```

---

## Configuration

Environment variables are set in `template.yaml` under `Globals.Function.Environment.Variables`.

| Variable | Default in template | Description |
|---|---|---|
| `STORAGE_IMPLEMENTATION` | `IN_FILE` | Storage backend: `IN_MEMORY` or `IN_FILE` |
| `STORAGE_FILE_PATH` | `/tmp/fileStorage.json` | Path to the JSON storage file (inside the container; `/tmp` is writable in Lambda) |
| `LOG_LEVEL` | `20` (INFO) | Python logging level |
| `OIDC_AUTH_ENABLED` | not set (defaults to `False`) | Set to `"true"` to enable OIDC/JWT validation |

To change a value, edit `template.yaml` and re-run `./run-sam-local.sh`.

> **Note:** With `IN_FILE` storage, data persists only for the lifetime of the
> running container. The file is written to `/tmp` inside the container and is
> lost when SAM stops.

---

## Rebuilding after code changes

SAM caches the built image. After changing Python source files or
`requirements-lambda.txt`, force a rebuild:

```bash
sam.cmd build --no-cached
```

Or simply re-run the script — `sam.cmd build` always rebuilds if sources have
changed.
