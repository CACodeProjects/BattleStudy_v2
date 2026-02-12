# Wizard Battle Study Game

A Flask-based quiz battle game where a player answers cybersecurity scenario questions to defeat a wizard.

## Features

- **Battle gameplay loop** with HP, streaks, XP, and win/lose states.
- **World (chapter) selection** to focus on subsets of questions.
- **Adaptive question difficulty** using per-question mistakes and difficulty levels.
- **Question progress tracking** in SQL with cooldown/completion behavior.
- **Session-based game state** for active battles.
- **Flask-Migrate support** for database schema migrations.

## Tech Stack

- Python 3.10+
- Flask
- Flask-SQLAlchemy
- Flask-Migrate (Alembic)
- Jinja2 templates
- SQLite (default) or PostgreSQL via `DATABASE_URL`

## Project Structure

```text
.
├── app.py                        # Flask app + routes + game logic
├── models.py                     # SQLAlchemy models
├── requirements.txt              # Python dependencies
├── templates/
│   ├── index.html                # Username entry page
│   ├── choose_world.html         # Chapter/world selection page
│   └── battle.html               # Main battle UI
├── data/
│   └── Questions_Scenario_Based_v5.json
├── migrations/                   # Alembic migration environment
└── instance/
    └── default.db                # Local SQLite DB (if using sqlite)
```

## How Gameplay Works

1. Player enters a username.
2. Player chooses a world/chapter.
3. A random eligible question is shown.
4. Correct answers damage wizard and grant XP.
5. Incorrect answers damage player and increase that question difficulty.
6. Progress per question is saved (`cooldown`, `mistakes`, `difficulty_level`, `completed`).

## Data Model

### `User`

- `id`
- `username` (unique)
- `email` (unique)
- `xp`

### `QuestionProgress`

- `id`
- `user_id` (FK to `User`)
- `question_id`
- `cooldown`
- `mistakes`
- `difficulty_level`
- `chapter`
- `completed`

## Prerequisites

- Python 3.10+ installed
- `pip` available

## Local Setup

### 1) Clone and enter project

```bash
git clone <your-repo-url>
cd BattleStudy_v2
```

### 2) Create and activate virtual environment

**macOS/Linux**

```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Configure environment variables

Create a `.env` file in project root:

```env
FLASK_SECRET_KEY=replace-with-a-strong-random-string
DATABASE_URL=sqlite:///default.db
FLASK_DEBUG=false
```

Notes:

- If `DATABASE_URL` is omitted, app falls back to `sqlite:///default.db`.
- Use PostgreSQL in production, e.g.:
  - `DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname`

### 5) Initialize database

If running first time:

```bash
python app.py
```

`app.py` runs `db.create_all()` on startup.

If using migrations workflow:

```bash
flask db upgrade
```

## Run the App

```bash
python app.py
```

App URLs:

- Local machine: `http://127.0.0.1:5000`
- LAN (same network): printed at startup by `app.py`

## Database Migrations

Common commands:

```bash
flask db init
flask db migrate -m "describe change"
flask db upgrade
flask db downgrade
```

> `flask db init` should only be run once per repository (already present here).

## Testing / Validation

Current lightweight checks:

```bash
python -m py_compile app.py models.py
python -m pytest -q
```

If `pytest` reports no tests found, that means automated tests have not yet been added.

## Deploying to Render

A basic `render.yaml` is included and currently starts with:

```yaml
startCommand: python app.py
```

For production hardening, prefer:

- `gunicorn app:app` as start command
- non-debug configuration
- managed PostgreSQL
- secure `FLASK_SECRET_KEY`

## Security Notes

- Never use the default development secret key in production.
- Keep `FLASK_DEBUG=false` in deployed environments.
- Set a strong, random `FLASK_SECRET_KEY`.
- Store secrets in platform environment settings, not source control.

## Troubleshooting

### App starts but pages error

- Ensure dependencies are installed in the active virtual environment.
- Check `DATABASE_URL` format.
- Run `flask db upgrade` if schema is behind.

### Username/session issues

- Clear browser cookies/session and retry.
- Restart the app after config changes.

### Dependency install issues

- Upgrade pip: `python -m pip install --upgrade pip`
- Recreate venv and reinstall requirements.

## Roadmap Suggestions

- Add automated tests (route tests + gameplay logic tests).
- Add CSRF protection for forms.
- Add account authentication beyond simple username.
- Move game logic into service modules for cleaner unit testing.

## Contributing

1. Create a feature branch.
2. Make focused commits.
3. Open a pull request into `main`.
4. Include test/validation output in PR description.

## License

Add your preferred license (MIT, Apache-2.0, etc.) in a `LICENSE` file.
