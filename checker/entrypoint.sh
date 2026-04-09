#!/bin/sh
set -eu

pip install --no-cache-dir -r /app/requirements.txt >/tmp/checker-pip-install.log

exec "$@"
