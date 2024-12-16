#!/bin/bash
if [ "$1" == "python" ]; then
  exec "$@"
fi
exec "$@"