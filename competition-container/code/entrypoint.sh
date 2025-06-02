#!/bin/bash
set -e

# Activate the venv
source /opt/venv/bin/activate

# If a requirements.txt exists in /mnt/user-code, install it
if [ -f /mnt/user-code/requirements.txt ]; then
  echo "[ENTRYPOINT] Installing user requirements..."
  pip install -r /mnt/user-code/requirements.txt
fi

# Change to user code directory if it exists
if [ -d "/mnt/user-code" ]; then
    cd /mnt/user-code
fi

# Exec the passed command (default to bash if none)
exec "$@"
