#!/usr/bin/env bash

set -e

echo "Run wsgi!!"

gunicorn --bind 0.0.0.0:${APP_PORT} app:server