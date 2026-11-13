# Self-hosted Mealie (family recipes)

Template repository to run [Mealie](https://github.com/mealie-recipes/mealie) on a small VPS with Docker Compose, nginx, and TLS. Fork or copy it for your own household—**do not commit secrets or recipe exports**.

## What you get

- Mealie v2 with PostgreSQL
- Bind to localhost only; expose via nginx + HTTPS
- Sensible `.gitignore` so `.env`, backups, and data stay off git

## Quick start (VPS)

```bash
sudo mkdir -p /opt/mealie && cd /opt/mealie
git clone <your-fork-url> .
cp .env.example .env
# Edit .env: BASE_URL and POSTGRES_PASSWORD (openssl rand -hex 32)
docker compose pull
docker compose up -d
```

Confirm Mealie responds:

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9925/
```

### nginx + HTTPS

1. Copy and edit `nginx/recipes.conf.example` for your domain.
2. Enable the site and obtain a certificate (Let's Encrypt example):

```bash
sudo certbot --nginx -d recipes.example.com
sudo nginx -t && sudo systemctl reload nginx
```

### First login

1. Open your `BASE_URL` in a browser.
2. Create the first admin account (signup is disabled for everyone else when `ALLOW_SIGNUP=false`).
3. Add categories per [docs/meal-categories.md](docs/meal-categories.md).

## Cloudflare (optional)

- Point an `A` record at your VPS.
- For orange-cloud proxy: use **Full** SSL with a valid cert on the origin (Let's Encrypt or [Cloudflare origin certificate](https://developers.cloudflare.com/ssl/origin-configuration/origin-ca/)).

## GrokBot

GrokBot uses a dedicated Mealie user and long-lived API token. Setup, env vars, and curl examples: **[docs/grokbot-integration.md](docs/grokbot-integration.md)**.

```bash
# On the VPS (see doc for MEALIE_ADMIN_* env vars)
python3 scripts/create-grokbot-user.py
```

Recipe categories for planning: [docs/meal-categories.md](docs/meal-categories.md).

## Backup

On the VPS:

```bash
cd /opt/mealie
docker compose exec -T postgres pg_dump -U mealie mealie > backups/mealie-$(date +%F).sql
```

Keep `backups/` out of git (already in `.gitignore`).

## License

MIT — see [LICENSE](LICENSE). Mealie itself is AGPL; this repo only contains deployment templates.
