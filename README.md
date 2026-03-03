# Wizard Battle Study Game

A Flask-based quiz battle game where a player answers cybersecurity scenario questions to defeat a wizard.

## Features

- Battle gameplay loop with HP, streaks, XP, and win/lose states.
- World (chapter) selection to focus on subsets of questions.
- Adaptive question difficulty using per-question mistakes and difficulty levels.
- Question progress tracking in SQL with cooldown/completion behavior.
- Session-based game state for active battles.

## Tech Stack

- Python 3.10+
- Flask
- Flask-SQLAlchemy
- SQLite (default) or PostgreSQL via `DATABASE_URL`

## Project Structure

```text
.
|-- app.py
|-- models.py
|-- requirements.txt
|-- templates/
|   |-- index.html
|   |-- choose_world.html
|   `-- battle.html
|-- data/
|   `-- Questions_Scenario_Based_v5.json
`-- instance/
    `-- default.db
```

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

## Local Setup

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `.env` in project root:

```env
FLASK_SECRET_KEY=replace-with-a-strong-random-string
DATABASE_URL=sqlite:///default.db
FLASK_DEBUG=false
```

## Run the App

```bash
python app.py
```

`app.py` runs `db.create_all()` on startup.

## Deploying to Render

Current `render.yaml` starts with:

```yaml
startCommand: python app.py
```

You can switch to Gunicorn for production if desired.

## Security Notes

- Never use the default development secret key in production.
- Keep `FLASK_DEBUG=false` in deployed environments.
- Set a strong, random `FLASK_SECRET_KEY`.
- Store secrets in platform environment settings, not source control.