#!/usr/bin/env bash
# Start the full VTN stack: MQTT broker + VTN-RI + optional callback service.
#
# Usage: bin/stack-start.sh [--with-callback] [--no-mqtt]
#
# Environment variables:
#   MQTT_START_CMD   — Command to start/restart the MQTT broker.
#                      Default: auto-detects brew (macOS) or systemctl (Linux).
#                      Set to "none" to skip broker management entirely
#                      (e.g. when using a remote broker).
#   VTN_CONFIG       — Path to config.yaml (default: config.yaml)
#   CALLBACK_DIR     — Path to test-callback-service repo
#                      (default: ../test-callback-service)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VTN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WITH_CALLBACK=false
START_MQTT=true

for arg in "$@"; do
    case "$arg" in
        --with-callback) WITH_CALLBACK=true ;;
        --no-mqtt) START_MQTT=false ;;
    esac
done

# --- MQTT broker ---
if [ "$START_MQTT" = true ]; then
    MQTT_CMD="${MQTT_START_CMD:-}"

    if [ -z "$MQTT_CMD" ]; then
        # Auto-detect
        if command -v brew &>/dev/null; then
            MQTT_CMD="brew services restart mosquitto"
        elif command -v systemctl &>/dev/null; then
            MQTT_CMD="sudo systemctl restart mosquitto"
        fi
    fi

    if [ "$MQTT_CMD" = "none" ]; then
        echo "MQTT broker management skipped (MQTT_START_CMD=none)."
    elif [ -n "$MQTT_CMD" ]; then
        echo "Starting MQTT broker: $MQTT_CMD"
        eval "$MQTT_CMD" 2>/dev/null || echo "Warning: MQTT broker start command failed."
        sleep 1
    else
        echo "Warning: could not detect MQTT broker service manager."
        echo "Set MQTT_START_CMD or ensure Mosquitto is running on port 1883."
    fi
fi

# --- VTN-RI ---
"$SCRIPT_DIR/vtn-start.sh" "${VTN_CONFIG:-config.yaml}"

# --- Callback service (optional) ---
if [ "$WITH_CALLBACK" = true ]; then
    CBS_DIR="${CALLBACK_DIR:-$(cd "$VTN_DIR/../test-callback-service" 2>/dev/null && pwd)}" || true
    CBS_SESSION="vtn-callbk-svc"

    if [ -z "$CBS_DIR" ] || [ ! -d "$CBS_DIR" ]; then
        echo "Warning: test-callback-service not found."
        echo "Set CALLBACK_DIR to the path of the test-callback-service repo."
    elif tmux has-session -t "$CBS_SESSION" 2>/dev/null; then
        echo "$CBS_SESSION is already running."
    else
        # Check/create venv
        if ! "$CBS_DIR/venv/bin/python3" --version &>/dev/null; then
            echo "Creating callback service venv..."
            python3.10 -m venv "$CBS_DIR/venv"
            "$CBS_DIR/venv/bin/pip" install -q -r "$CBS_DIR/requirements.txt"
        fi
        echo "Starting $CBS_SESSION..."
        tmux new-session -d -s "$CBS_SESSION" \
            "cd '$CBS_DIR' && source venv/bin/activate && python3 run.py 2>&1 | tee /tmp/vtn-callbk-svc.log"
        sleep 1
        echo "$CBS_SESSION started — http://localhost:5000"
    fi
fi

echo ""
echo "Stack is up."
