#!/bin/bash
# Helper to build+run container, cuz this incantation is messy

if [ "${MUSIC_DIR}" == "" ]; then
  echo "Please set your MUSIC_DIR env var"
fi

docker build -t djtaytay:latest .
docker run -p 8000:8000 --mount type=bind,source="${MUSIC_DIR}",target=/data,readonly djtaytay:latest
