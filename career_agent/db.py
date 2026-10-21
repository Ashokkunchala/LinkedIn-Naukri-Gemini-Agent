import sqlite3
from contextlib import contextmanager

from .config import DATABASE_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs(
 id INTEGER PRIMARY KEY, platform TEXT NOT NULL, title TEXT NOT NULL,
 company TEXT NOT NULL DEFAULT '', location TEXT NOT NULL DEFAULT '', url TEXT NOT NULL DEFAULT '',
 description TEXT NOT NULL, fit_score INTEGER NOT NULL DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS approvals(
 id INTEGER PRIMARY KEY, action_type TEXT NOT NULL, target TEXT NOT NULL, payload TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'pending', requested_at TEXT DEFAULT CURRENT_TIMESTAMP,
 decided_at TEXT, decision_note TEXT
);
CREATE TABLE IF NOT EXISTS applications(
 id INTEGER PRIMARY KEY, job_id INTEGER NOT NULL, status TEXT NOT NULL, notes TEXT NOT NULL DEFAULT '',
 updated_at TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(job_id) REFERENCES jobs(id)
);
CREATE TABLE IF NOT EXISTS audit_log(
 id INTEGER PRIMARY KEY, event_type TEXT NOT NULL, detail TEXT NOT NULL,
 created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

@contextmanager
def connect():
    con = sqlite3.connect(DATABASE_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    try:
        yield con
        con.commit()
    finally:
        con.close()

def init_db():
    with connect() as con:
        con.executescript(SCHEMA)

def audit(event, detail):
    with connect() as con:
        con.execute("INSERT INTO audit_log(event_type,detail) VALUES(?,?)", (event, detail))
