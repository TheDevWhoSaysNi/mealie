# Meal categories for planner automation

Mealie uses **categories** and **tags** on recipes. Use categories for the meal *slot* and tags for finer labels (kid-friendly, batch-prep, etc.).

## Recommended categories

Create these in **Settings → Organize → Categories** (names are up to you; keep them consistent for automation):

| Category        | Use for                          |
|-----------------|----------------------------------|
| Breakfast       | Morning meals                    |
| Lunch           | Midday meals                     |
| Dinner          | Evening meals                    |
| Dessert         | Sweets and treats                |
| Appetizer       | Starters, snacks for guests      |
| Side dish       | Sides that pair with mains       |
| Vegetables      | Veg-forward dishes               |
| Bulk / prep     | Club runs, freezer batch cooking |

## Meal planner workflow

1. Add recipes and assign exactly one primary category per recipe (or use tags if a recipe fits multiple slots).
2. Open **Meal Planner** and drag recipes onto days, or use **random** / rule-based planning if you add integrations later.
3. Generate a **shopping list** from the planned week.

## API & automation (optional)

Mealie exposes a REST API. After you create an admin user:

1. **Profile → API Tokens** — create a token for automation (GrokBot, scripts).
2. Base URL: `{BASE_URL}/api`
3. Common endpoints: `/api/recipes`, `/api/households/mealplans`, `/api/organizers/categories`

Do not store API tokens in this repository; keep them in your password manager or GrokBot secret store.
