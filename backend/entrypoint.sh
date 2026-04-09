#!/bin/sh
set -eu

pip install --no-cache-dir -r /app/requirements.txt >/tmp/backend-pip-install.log

exec "$@"
