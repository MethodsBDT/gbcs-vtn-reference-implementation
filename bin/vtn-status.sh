#!/usr/bin/env bash
# Check VTN-RI status.

SESSION="vtn-ri"

if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "$SESSION: running (tmux session active)"
else
    echo "$SESSION: stopped"
    exit 1
fi

# Check HTTP
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/openadr3/3.1.0/programs 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "000" ]; then
    echo "HTTP: not responding"
    exit 1
elif [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
    echo "HTTP: responding ($HTTP_CODE)"
else
    echo "HTTP: unexpected status ($HTTP_CODE)"
fi
