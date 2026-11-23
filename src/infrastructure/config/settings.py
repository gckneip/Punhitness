import os
from pathlib import Path

DATA_DIR = Path(os.path.expanduser("~")) / ".gym_tracker"
THEMES_DIR = DATA_DIR / "themes"

# gym-tracker has two independent entrypoints (the Qt app and the MCP server,
# which an AI client launches as its own subprocess) that must resolve to the
# same DB file with no shared runtime state to coordinate through — an env
# var lets both agree on an alternate path for sandboxing/testing.
_override = os.environ.get("GYM_TRACKER_DB_PATH")
DB_PATH = Path(_override) if _override else DATA_DIR / "gym.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
THEMES_DIR.mkdir(parents=True, exist_ok=True)
