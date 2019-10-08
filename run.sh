#!/bin/bash
# Helper to build+run container, cuz this incantation is messy

source .env

if [ "${MUSIC_DIR}" == "" ]; then
  echo "Please set your MUSIC_DIR env var"
  exit 1
fi

docker build -t djtaytay:latest .
docker run -p 8000:8000 \
  --mount type=bind,source="${MUSIC_DIR}",target="${MUSIC_DIR}",readonly \
  djtaytay:latest
