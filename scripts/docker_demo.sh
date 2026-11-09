#!/usr/bin/env bash
# Construye la imagen, corre el contenedor y muestra el estado y los logs.
# Uso (desde la raíz del repositorio):  bash scripts/docker_demo.sh
set -euo pipefail

IMAGE=intencion-compra-app
NAME=intencion-compra

titulo() { printf '\n\033[1;32m==== %s ====\033[0m\n' "$1"; }

titulo "1. docker build"
docker build -t "$IMAGE" .

titulo "2. docker images"
docker images "$IMAGE"

titulo "3. docker run"
docker rm -f "$NAME" >/dev/null 2>&1 || true
docker run -d --name "$NAME" -p 8501:8501 "$IMAGE"

titulo "4. docker ps"
sleep 6
docker ps --filter "name=$NAME"

titulo "5. docker logs"
docker logs "$NAME"

titulo "Listo"
echo "La app está en el puerto 8501. Para detenerla: docker stop $NAME"
