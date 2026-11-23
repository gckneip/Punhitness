import sqlite3
from src.infrastructure.config.settings import DB_PATH


def get_connection() -> sqlite3.Connection:
    # check_same_thread=False: the MCP server dispatches each tool call onto a
    # worker-thread pool (see mcp_server.py), while the connection is opened
    # once on the main thread. The Qt app stays single-threaded regardless, so
    # this only relaxes a check that would otherwise never trigger there.
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn
