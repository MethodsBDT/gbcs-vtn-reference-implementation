#!/usr/bin/env bash
# Stop the VTN-RI tmux session.

SESSION="vtn-ri"

if tmux kill-session -t "$SESSION" 2>/dev/null; then
    echo "$SESSION stopped."
else
    echo "$SESSION is not running."
fi
