# GrokBot / agent integration

Connect an agent (for example a “Food” GrokBot) to Mealie after the stack is running.

## 1. Create an API token

1. Log into Mealie as an admin.
2. Open your **profile → API tokens** (or **Settings → API** depending on version).
3. Create a token with a clear label (for example `grokbot-food`).
4. Store the token in your agent secret store — **not** in this git repo.

## 2. Base URL

- Web UI: value of `BASE_URL` in your VPS `.env`
- API: `{BASE_URL}/api/docs` for interactive OpenAPI docs

## 3. Categories align with your meal list

Mirror the sheets or lists you already use (breakfast, lunch, dinner, etc.) as Mealie categories. See [meal-categories.md](./meal-categories.md).

Typical agent tasks:

- `GET /api/recipes` — search and list
- `POST /api/recipes` — add from URL or structured JSON
- Meal plan endpoints under `/api/households/.../mealplans`

## 4. Household access

Invite family members from **Settings → Household**. The agent token should belong to an admin or a dedicated automation user with the right household scope.

## 5. Rate limits and safety

Run imports in batches. Prefer idempotent scripts (check by slug or title before create). Keep recipe exports and backups out of git (see root `.gitignore`).
