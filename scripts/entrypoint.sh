#!/bin/bash

# Check AUTOSTART environment variable
if [ -n "$AUTOSTART" ]; then
  echo "AUTOSTART is set. Starting Flask server with system python."
  exec /usr/local/bin/python3.11 server.py
else
  echo "AUTOSTART is not set. Container will not start the server."
  exit 0
fi 