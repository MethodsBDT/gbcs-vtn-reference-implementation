#!/usr/bin/env bash
# Bootstrap Mosquitto with the dynamic security plugin for OpenADR VTN-RI.
#
# Reads broker credentials from config.yaml, generates:
#   1. A mosquitto config file with the dynsec plugin enabled
#   2. A dynamic-security.json with the VTN admin user and static roles/ACLs
#
# Usage:
#   bin/bootstrap-mosquitto-dynsec.sh [config-file]
#
# The generated files are written to cfg/mosquitto/dynsec/.
# After running this script, start mosquitto with:
#   mosquitto -c cfg/mosquitto/dynsec/mosquitto-dynsec.conf

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VTN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="${1:-${VTN_CONFIG:-config.yaml}}"
OUTPUT_DIR="$VTN_DIR/cfg/mosquitto/dynsec"

if [ ! -f "$VTN_DIR/$CONFIG_FILE" ] && [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: config file not found: $CONFIG_FILE"
    exit 1
fi

# Resolve to absolute path
if [ -f "$VTN_DIR/$CONFIG_FILE" ]; then
    CONFIG_FILE="$VTN_DIR/$CONFIG_FILE"
fi

echo "Reading configuration from: $CONFIG_FILE"
echo "Output directory: $OUTPUT_DIR"

mkdir -p "$OUTPUT_DIR"

# --- Activate project venv if available ---
if [ -f "$VTN_DIR/venv/bin/activate" ]; then
    source "$VTN_DIR/venv/bin/activate"
fi

# --- Find the dynsec plugin path ---
DYNSEC_PLUGIN=""
for candidate in \
    /opt/homebrew/lib/mosquitto_dynamic_security.so \
    /usr/local/lib/mosquitto_dynamic_security.so \
    /usr/lib/mosquitto_dynamic_security.so \
    /usr/lib/x86_64-linux-gnu/mosquitto_dynamic_security.so \
    /usr/lib/aarch64-linux-gnu/mosquitto_dynamic_security.so; do
    if [ -f "$candidate" ]; then
        DYNSEC_PLUGIN="$candidate"
        break
    fi
done

if [ -z "$DYNSEC_PLUGIN" ]; then
    echo "Error: Could not find mosquitto_dynamic_security.so"
    echo "Install mosquitto with dynsec support, or set DYNSEC_PLUGIN_PATH."
    exit 1
fi

DYNSEC_PLUGIN="${DYNSEC_PLUGIN_PATH:-$DYNSEC_PLUGIN}"
echo "Using dynsec plugin: $DYNSEC_PLUGIN"

# --- Generate dynamic-security.json and mosquitto config via Python ---
python3 - "$CONFIG_FILE" "$OUTPUT_DIR" "$DYNSEC_PLUGIN" <<'PYTHON_SCRIPT'
import sys
import os
import json
import hashlib
import base64
import secrets

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

config_file = sys.argv[1]
output_dir = sys.argv[2]
dynsec_plugin = sys.argv[3]

with open(config_file) as f:
    cfg = yaml.safe_load(f)

mqtt_cfg = cfg.get('mqtt', {}).get('broker', {})
broker_host = mqtt_cfg.get('host', '127.0.0.1')
broker_port = mqtt_cfg.get('port', 1883)
admin_username = mqtt_cfg.get('username')
admin_password = mqtt_cfg.get('password')

if not admin_username or not admin_password:
    print("Error: mqtt.broker.username and mqtt.broker.password must be set in config.yaml", file=sys.stderr)
    sys.exit(1)

# --- Password hashing (PBKDF2-SHA512, matching mosquitto dynsec encoded_password format) ---
# Mosquitto v2.x uses: $7$iterations$base64_salt$base64_hash
def encode_password(password, iterations=1000):
    salt = secrets.token_bytes(12)
    dk = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, iterations, dklen=64)
    salt_b64 = base64.b64encode(salt).decode('ascii')
    hash_b64 = base64.b64encode(dk).decode('ascii')
    return f"$7${iterations}${salt_b64}${hash_b64}"

# --- Topic base paths from config ---
topics = cfg.get('mqtt', {}).get('topics', {})
programs_base = topics.get('programs', 'programs')
events_base = topics.get('events', 'events')
reports_base = topics.get('reports', 'reports')
subscriptions_base = topics.get('subscriptions', 'subscriptions')
vens_base = topics.get('vens', 'vens')
resources_base = topics.get('resources', 'resources')

# --- Define static roles ---
roles = [
    {
        "roleName": "vtn-publisher",
        "acls": [
            {"acltype": "publishClientSend", "topic": "#", "priority": 0, "allow": True},
            {"acltype": "publishClientSend", "topic": "$CONTROL/dynamic-security/v1", "priority": 0, "allow": True},
            {"acltype": "subscribePattern", "topic": "$CONTROL/dynamic-security/v1/response", "priority": 0, "allow": True},
            {"acltype": "publishClientReceive", "topic": "$CONTROL/dynamic-security/v1/response", "priority": 0, "allow": True},
        ]
    },
    {
        "roleName": "bl-subscriber",
        "acls": [
            {"acltype": "subscribePattern", "topic": f"{programs_base}/#", "priority": 0, "allow": True},
            {"acltype": "subscribePattern", "topic": f"{events_base}/#", "priority": 0, "allow": True},
            {"acltype": "subscribePattern", "topic": f"{reports_base}/#", "priority": 0, "allow": True},
            {"acltype": "subscribePattern", "topic": f"{subscriptions_base}/#", "priority": 0, "allow": True},
            {"acltype": "subscribePattern", "topic": f"{vens_base}/#", "priority": 0, "allow": True},
            {"acltype": "subscribePattern", "topic": f"{resources_base}/#", "priority": 0, "allow": True},
        ]
    },
    {
        "roleName": "ven-base",
        "acls": [
            {"acltype": "subscribePattern", "topic": f"{programs_base}/+", "priority": 0, "allow": True},
            {"acltype": "subscribePattern", "topic": f"{events_base}/+", "priority": 0, "allow": True},
            {"acltype": "subscribePattern", "topic": f"{reports_base}/+", "priority": 0, "allow": True},
            {"acltype": "subscribePattern", "topic": f"{subscriptions_base}/+", "priority": 0, "allow": True},
        ]
    },
]

# --- Build the dynamic-security.json ---
dynsec = {
    "clients": [
        {
            "username": admin_username,
            "textName": "VTN admin user",
            "encoded_password": encode_password(admin_password),
            "roles": [
                {"rolename": "vtn-publisher", "priority": -1}
            ]
        }
    ],
    "groups": [],
    "roles": roles,
    "defaultACLAccess": {
        "publishClientSend": False,
        "publishClientReceive": True,
        "subscribe": False,
        "unsubscribe": True
    }
}

# --- Write dynamic-security.json ---
dynsec_json_path = os.path.join(output_dir, "dynamic-security.json")
with open(dynsec_json_path, 'w') as f:
    json.dump(dynsec, f, indent=2)
    f.write('\n')
print(f"Generated: {dynsec_json_path}")

# --- Write mosquitto-dynsec.conf ---
dynsec_conf_path = os.path.join(output_dir, "mosquitto-dynsec.conf")
with open(dynsec_conf_path, 'w') as f:
    f.write(f"""\
# Mosquitto configuration with dynamic security plugin
# Generated by bootstrap-mosquitto-dynsec.sh — do not edit manually.

listener {broker_port} {broker_host}
allow_anonymous false

plugin {dynsec_plugin}
plugin_opt_config_file {os.path.abspath(dynsec_json_path)}
""")
print(f"Generated: {dynsec_conf_path}")

print()
print(f"Admin username: {admin_username}")
print(f"Broker: {broker_host}:{broker_port}")
print()
print("To start mosquitto with dynsec:")
print(f"  mosquitto -c {dynsec_conf_path}")
PYTHON_SCRIPT

echo ""
echo "Bootstrap complete."
