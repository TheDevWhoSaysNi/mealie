#!/usr/bin/env bash
# Run on the VPS as root after cloning this repo into /opt/mealie.
set -euo pipefail

INSTALL_DIR="${1:-/opt/mealie}"
cd "$INSTALL_DIR"

if [[ ! -f .env ]]; then
  cp .env.example .env
  pw="$(openssl rand -hex 24)"
  if grep -q '^POSTGRES_PASSWORD=change-me' .env; then
    sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=${pw}/" .env
  fi
  echo "Created .env with generated POSTGRES_PASSWORD. Set BASE_URL before going live."
fi

docker compose pull
docker compose up -d

echo "Mealie local: http://127.0.0.1:${MEALIE_PORT:-9925}"

