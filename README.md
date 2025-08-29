<div align="center">

# 💸 MoneyFlow
Simple personal money tracker built with **Django + Tailwind (CDN) + SQLite**. Fast to spin up, pleasant to use, easy to extend.

</div>

## Why this exists
I wanted a tiny finance tool that gives me: a quick glance at income vs expense, frictionless transaction entry, dark mode that sticks, and zero build tooling. MoneyFlow is intentionally minimal but structured so you can grow it (exporting, reports, richer analytics, etc.).

## Core Features
| Area | What you get |
|------|--------------|
| Auth | Register, login, logout, password reset (console backend for now) |
| Dashboard | Income / Expense / Balance KPIs + recent transactions |
| Transactions | Create, edit, delete; filter by type, date range, category; search notes/category |
| Categories | Starter defaults (Salary, Food, Rent, etc.) + add your own |
| UI / UX | Mobile‑friendly, dark/light theme toggle (persists), responsive nav, accessible forms |
| Styling | Tailwind via CDN, gradient summary cards, status badges |
| Other | Pagination, session + localStorage theme cohesion |

## Quick Start
```bash
# 1. Create & activate a virtual environment (using uv)
uv venv .venv
source .venv/bin/activate

# 2. Install dependencies
uv pip install -r requirements.txt

# 3. Apply migrations
python manage.py migrate

# 4. Run the dev server
python manage.py runserver 127.0.0.1:8000
```
Open: http://127.0.0.1:8000/

Optional admin user:
```bash
python manage.py createsuperuser
```
Admin: http://127.0.0.1:8000/admin/

## Project Layout (essentials)
```
moneyflow/
	moneyflow/settings.py      ← configuration
	core/
		models.py                ← Category, Transaction
		forms.py                 ← Registration, Transaction, Category, styled auth
		views.py                 ← dashboard, CRUD, profile, about, login view
		templatetags/            ← optional custom filters (currently unused)
	templates/
		base.html                ← layout, nav, theme script
		registration/            ← auth templates
		core/                    ← dashboard, transactions, profile, etc.
```

## Data Model
| Model | Key Fields | Notes |
|-------|------------|-------|
| Category | name, user (nullable), is_default | Default rows are global; user rows are personal |
| Transaction | user, type (income/expense), category, amount, date, notes | Ordered newest first |

## Theme Logic
User toggles theme → class stored in session + localStorage. On load, the server injects current theme, then client script ensures consistency. No FOUC for most scenarios.

## Password Reset
Uses Django console email backend: click “Forgot password?”, then read the terminal output for the reset link.

## Roadmap Ideas
Small, safe improvements you can tackle next:
1. CSV export of filtered transactions
2. Basic test suite (auth, CRUD, filters)
3. Tailwind build (PurgeCSS) for production footprint
4. Category edit & delete
5. Monthly summary / simple charts
6. Docker + Gunicorn + whitenoise setup

## Production Hardening Checklist
- Set `DEBUG = False`
- Rotate `SECRET_KEY` → use env var
- Add real email backend (SMTP / provider)
- Serve static files (whitenoise or CDN)
- Enforce HTTPS (proxy headers, `SECURE_*` settings)
- Add CSP / security headers
- Database backup & monitoring plan

## Contributing / Extending
Fork it, add a feature (e.g., export, charts, budgets), open a PR or keep it personal. Keep UI changes consistent: utility classes + minimal custom CSS.

### Adding a dependency
Add the package with uv, then freeze requirements:
```bash
uv pip install <package>
uv pip freeze > requirements.txt
```

## License
MIT (add LICENSE file if distributing publicly).

---
Built for quick personal finance tracking. Tweak it to match how you think about money.
