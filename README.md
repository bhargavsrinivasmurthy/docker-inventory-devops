# Docker Inventory DevOps

A small inventory management system built with Python Flask and SQLite, being developed step by step as a DevOps portfolio project. Docker, Docker Compose and GitHub Actions CI are planned next.

## Current status

**Verified so far (tested locally on Windows):**
- Flask app factory with SQLite persistence through Flask-SQLAlchemy
- Product and stock-transaction models with a non-negative stock constraint
- Business logic for creating products, stock receipts, sales and audited adjustments
- Overselling is rejected and each stock change is saved together with its audit record
- 10 automated pytest tests passing, Ruff lint clean
- Web interface checked manually in the browser: dashboard, product list, add product, stock operations, low-stock warning and transaction history

**Not built yet:**
- CSRF protection on forms
- Product editing (create, search and deactivate exist)
- Dockerfile, Docker Compose, health check container setup
- GitHub Actions CI workflow
- Backup and restore scripts
- Security scan documentation

## Tech stack

Python 3.13 (local; Python 3.12 is planned for the Docker image), Flask, Flask-SQLAlchemy, SQLite, Bootstrap 5 (CDN), pytest, Ruff, Git and GitHub.

## Project structure

```
docker-inventory-devops/
  app.py                 launcher that starts the app
  app/
    __init__.py          app factory and database setup
    models.py            Product and InventoryTransaction tables
    services.py          validated stock and product logic
    routes.py            web pages and the /health endpoint
    templates/           base, dashboard, products, product_form, stock, transactions
  tests/
    conftest.py          in-memory test database fixtures
    test_inventory.py    10 tests for the stock logic
  requirements.txt
  .gitignore
```

## Setup on Windows (PowerShell)

```
git clone https://github.com/bhargavsrinivasmurthy/docker-inventory-devops.git
cd docker-inventory-devops
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 in a browser.

If PowerShell refuses to activate the virtual environment, allow local scripts for your user only:

```
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## Running the tests and lint

```
python -m pytest -v
python -m ruff check .
```

## Pages

- `/` dashboard: product count, units in stock, low and out-of-stock counts, inventory value, recent transactions
- `/products` list with search by name or SKU
- `/products/new` add a product
- `/products/<id>/stock` receive, sell or adjust stock
- `/transactions` full audit history
- `/health` returns `{"status": "ok"}`

## Business rules

- SKU must be unique and required
- Prices and quantities cannot be negative
- Sale and receipt quantities must be positive
- Stock cannot go below zero
- Adjustments require a reason
- Every stock change records the before and after quantity

## How the project was built

1. Verified Python, Git, Docker, Docker Compose and WSL
2. Created the Flask starter app and ran it in a virtual environment
3. Initialised Git, added `.gitignore` (excludes `.venv`, `*.db`, `.env`)
4. Created the GitHub repository and pushed the first commit, resolving a rejected push with `git pull origin main --allow-unrelated-histories`
5. Added `requirements.txt` and this README
6. Installed Flask-SQLAlchemy, pytest and Ruff
7. Wrote the models, services and tests; fixed a SQLAlchemy legacy warning and three Ruff findings
8. Added routes and templates, then tested the full flow in the browser

## Known limitations

- Local demonstration only, not production ready
- No login, authorization or HTTPS
- Forms have no CSRF protection yet
- `SECRET_KEY` in `app/__init__.py` is a development placeholder and must come from an environment variable before any real use
- No database migrations yet
- Bootstrap loads from a CDN, so the pages need internet access

## Next steps

1. CSRF protection and product editing
2. Dockerfile with a non-root user, Gunicorn and a health check
3. Docker Compose with a named database volume
4. GitHub Actions workflow for lint, tests and Docker build
5. Backup and restore scripts with documented recovery
6. Security review and a client demonstration