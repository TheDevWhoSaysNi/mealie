# GrokBot setup (Mealie API)

Use a **dedicated Mealie user** for GrokBot so your family login stays separate from automation. GrokBot should call the public API with a **long-lived API token** (not your personal password).

## Values for GrokBot

Configure these in GrokBot’s secret store (or tool env vars):

| Variable | Example | Notes |
|----------|---------|--------|
| `MEALIE_BASE_URL` | `https://recipes.example.com` | No trailing slash |
| `MEALIE_API_TOKEN` | *(long JWT string)* | From `grokbot-credentials.json` on the VPS or Mealie UI |

**Auth header on every request:**

```http
Authorization: Bearer <MEALIE_API_TOKEN>
```

Interactive reference: `{MEALIE_BASE_URL}/docs` (OpenAPI / Swagger on your instance).

## Automated user (VPS)

On the server, after Mealie is running and you have an admin login:

```bash
cd /opt/mealie
export MEALIE_ADMIN_USERNAME=admin
export MEALIE_ADMIN_PASSWORD='your-admin-password'
export MEALIE_BASE_URL=http://127.0.0.1:9925
export MEALIE_PUBLIC_BASE_URL=https://recipes.example.com
python3 scripts/create-grokbot-user.py
sudo cat grokbot-credentials.json   # copy api_token to GrokBot only
```

Default bot username: `grokbot-food`. The script:

1. Creates the user (or updates an existing one).
2. Sets **Can organize** and **Can manage household** (recipes, meal plans, shopping lists).
3. Mints a long-lived token named `grokbot-food`.
4. Writes `grokbot-credentials.json` (mode `0600`, **gitignored**).

Override names with `MEALIE_BOT_USERNAME`, `MEALIE_BOT_EMAIL`, etc. (see script header).

## What GrokBot should do

You enter recipes (or ask GrokBot to import them). GrokBot handles **fill-out and maintenance**:

- Import from URLs: `POST /api/recipes/create/url`
- Create or update full recipes: `POST /api/recipes`, `PUT /api/recipes/{slug}`
- Categories and tags: `/api/organizers/categories`, `/api/organizers/tags`
- Meal plan: household meal plan endpoints under `/api/households/...`
- Shopping lists: `/api/households/shopping/lists` and related routes

Use **categories** that match your family lists (breakfast, lunch, dinner, etc.) — see [meal-categories.md](./meal-categories.md).

### Example: list recipes

```bash
curl -sS -H "Authorization: Bearer $MEALIE_API_TOKEN" \
  "$MEALIE_BASE_URL/api/recipes?perPage=20&page=1"
```

### Example: create from a URL

```bash
curl -sS -X POST -H "Authorization: Bearer $MEALIE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/some-recipe"}' \
  "$MEALIE_BASE_URL/api/recipes/create/url"
```

(Confirm the exact JSON shape in `/docs` for your Mealie version.)

## GrokBot tool configuration (suggested)

In the Food bot, add something like:

- **Mealie base URL** → `MEALIE_BASE_URL`
- **Mealie API token** → `MEALIE_API_TOKEN`
- Document that writes go to household **Family** (slug `family`) unless you change the bot user’s household in Mealie.

Prefer **idempotent** imports: search by title or slug before creating duplicates.

## Cloudflare

If GrokBot runs outside your home network, it hits the public URL. API calls with a Bearer token should return `200` from `GET /api/recipes`. If you see Cloudflare `1010` or challenge pages on `POST`, relax Bot Fight Mode for this subdomain or route GrokBot through a allowlisted IP.

## Security checklist

- Do **not** commit `grokbot-credentials.json`, `.env`, or tokens to git.
- Rotate the API token in Mealie (**Profile → API tokens**) if it leaks; re-run the script if you need a new bot password.
- Change the default Mealie `admin` password if you never did after install.
- Keep `ALLOW_SIGNUP=false` so only admins can add users.

## Household members

Family humans use their own Mealie accounts (invite from **Settings → Household**). Only GrokBot needs the API token.
