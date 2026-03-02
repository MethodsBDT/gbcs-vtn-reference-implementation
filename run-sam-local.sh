#!/usr/bin/env bash
set -euo pipefail

echo "==> Building Lambda image with SAM"
sam.cmd build --no-cached

echo ""
echo "==> Starting SAM local HTTP API on http://localhost:8080"
echo "    Example: curl http://localhost:8080/openadr3/3.1.0/programs"
echo "    Press Ctrl+C to stop."
echo ""

sam.cmd local start-api \
  --port 8080 \
  --warm-containers EAGER
