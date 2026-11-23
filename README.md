# 🏋️ Gym Tracker

A desktop fitness tracker built with **Python** and **PySide6 (Qt)**, backed by a local **SQLite** database. Log daily workout sessions, build reusable routines, track bodyweight, and watch your progress over time — all running offline on your machine.

A companion **MCP server** exposes your training log (read-only) to AI clients like Claude Code, Claude Desktop, or Codex, so you can ask for tips on your training regimen based on your actual history.

## ✨ Features

- **Dashboard** — sessions/week, current streak, last bodyweight, and progress charts
- **Exercises** — a reusable catalog (name, muscle group, equipment)
- **Routines** — predefined plans (e.g. "Push Day") with target sets/reps/weight per exercise
- **Log Session / History** — start a session from a routine or blank, fill in sets as you go, review past sessions
- **Body Metrics** — track bodyweight over time

## 🏗️ Architecture

Clean Architecture, same split as other projects in this family:

```
src/
├── domain/          # Entities, repository interfaces, business rules
├── application/      # Use cases and DTOs
├── infrastructure/    # SQLite repositories, schema, config
└── presentation/      # PySide6 windows/dialogs/widgets, and the MCP server
```

Your data is stored locally in `~/.gym_tracker/gym.db` — nothing leaves your machine unless you connect an AI client to the MCP server below.

## 🚀 Running

```bash
./gym-tracker
```

The launcher creates a `.venv` and installs dependencies automatically on first run.

### Manual setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python src/main.py
```

## 🤖 Connecting an AI for training tips

`src/mcp_server.py` is a second, headless entrypoint (no Qt) that exposes your training log over the Model Context Protocol via stdio. It only reads data — logging workouts still happens in the app.

Tools exposed: `list_exercises`, `list_routines`, `get_recent_sessions`, `get_exercise_history`, `get_body_metrics`, `get_training_summary`.

Run it directly via the `gym-tracker-mcp` launcher (same venv-bootstrapping as the main app):

```bash
./gym-tracker-mcp
```

**Claude Code:**

```bash
claude mcp add gym-tracker -- /path/to/gym-tracker/gym-tracker-mcp
```

**Claude Desktop** (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "gym-tracker": {
      "command": "/path/to/gym-tracker/gym-tracker-mcp"
    }
  }
}
```

**Codex CLI** (`~/.codex/config.toml`):

```toml
[mcp_servers.gym-tracker]
command = "/path/to/gym-tracker/gym-tracker-mcp"
```

### Sandboxing the database

Both entrypoints resolve the DB path from `src/infrastructure/config/settings.py`, which honors a `GYM_TRACKER_DB_PATH` environment variable override (falling back to `~/.gym_tracker/gym.db`). Useful for testing the MCP server or the app against a throwaway database:

```bash
GYM_TRACKER_DB_PATH=/tmp/gym-test.db ./gym-tracker-mcp
```

## 🧰 Tech Stack

- **Python 3**
- **PySide6** (Qt for Python) — desktop UI
- **pyqtgraph** — progress charts
- **SQLite** — local, file-based storage
- **mcp** — Model Context Protocol SDK for the AI-tips server

## 🧪 Tests

```bash
.venv/bin/python -m pytest
```

Pure unit tests over the domain services and application use cases, using hand-rolled fake repositories (no SQLite needed to run them).
