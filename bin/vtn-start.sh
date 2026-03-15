#!/usr/bin/env bash
# Start the VTN-RI in a tmux session.
# Usage: bin/vtn-start.sh [config.yaml]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VTN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SESSION="vtn-ri"
CONFIG="${1:-config.yaml}"
VENV_DIR="$VTN_DIR/venv"
LOG="/tmp/vtn-ri.log"

# Check tmux
if ! command -v tmux &>/dev/null; then
    echo "Error: tmux is required but not installed." >&2
    exit 1
fi

# Check if already running
if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "$SESSION is already running. Use bin/vtn-stop.sh first."
    exit 1
fi

# Check/create venv
if ! "$VENV_DIR/bin/python3" --version &>/dev/null; then
    echo "Creating venv (requires python3.10)..."
    if ! command -v python3.10 &>/dev/null; then
        echo "Error: python3.10 is required to create the venv." >&2
        exit 1
    fi
    rm -rf "$VENV_DIR"
    python3.10 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install -q 'setuptools<81'
    "$VENV_DIR/bin/pip" install -q -r "$VTN_DIR/requirements.txt"
fi

# Verify connexion imports
if ! "$VENV_DIR/bin/python3" -c "import connexion" &>/dev/null; then
    echo "Fixing dependencies..."
    "$VENV_DIR/bin/pip" install -q 'setuptools<81'
    "$VENV_DIR/bin/pip" install -q -r "$VTN_DIR/requirements.txt"
fi

# Start in tmux
echo "Starting $SESSION..."
tmux new-session -d -s "$SESSION" \
    "cd '$VTN_DIR' && source venv/bin/activate && ulimit -n 2048 && VTN_CONFIG='$CONFIG' python3 -m swagger_server 2>&1 | tee '$LOG'"

# Wait for startup
for i in $(seq 1 15); do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/openadr3/3.1.0/programs 2>/dev/null | grep -q "200\|401\|403"; then
        echo "$SESSION is up — http://localhost:8080/openadr3/3.1.0"
        echo "Log: $LOG"
        echo "Attach: tmux attach-session -t $SESSION"
        exit 0
    fi
    sleep 1
done

echo "Warning: $SESSION started but HTTP not responding after 15s."
echo "Check log: $LOG"
exit 1
