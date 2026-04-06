"""SQLite schema and connection — cloud-portable (swap DB_PATH for Supabase URL later)."""

import sqlite3
from pathlib import Path
from .config import DB_PATH


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_conn()
    conn.executescript("""

    -- ── Profile ──────────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS profile (
        key         TEXT PRIMARY KEY,
        value       TEXT NOT NULL,
        domain      TEXT DEFAULT 'general',
        confidence  REAL DEFAULT 1.0,          -- how sure we are (0-1)
        source      TEXT DEFAULT 'interview',  -- interview | passive | explicit
        updated_at  TEXT DEFAULT (datetime('now'))
    );

    -- ── Domain expertise levels ───────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS domains (
        name            TEXT PRIMARY KEY,
        expertise_level TEXT CHECK(expertise_level IN
                            ('curious','learning','knowledgeable','expert'))
                            DEFAULT 'curious',
        interest_level  INTEGER DEFAULT 5,     -- 1-10
        notes           TEXT,
        updated_at      TEXT DEFAULT (datetime('now'))
    );

    -- ── Base inventory table ──────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS inventory (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        domain          TEXT NOT NULL,         -- guns | gear | supplements | etc
        name            TEXT NOT NULL,
        brand           TEXT,
        model           TEXT,
        acquired_date   TEXT,
        condition       TEXT DEFAULT 'good',
        satisfaction    INTEGER,               -- 1-10, filled over time
        notes           TEXT,
        tags            TEXT,                  -- comma-separated
        created_at      TEXT DEFAULT (datetime('now')),
        updated_at      TEXT DEFAULT (datetime('now'))
    );

    -- ── Guns (extends inventory) ──────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS guns (
        inventory_id        INTEGER PRIMARY KEY REFERENCES inventory(id),
        serial_number       TEXT UNIQUE NOT NULL,
        type                TEXT,              -- pistol | rifle | shotgun | etc
        caliber             TEXT,
        manufacturer        TEXT,
        barrel_length_in    REAL,
        capacity            INTEGER,
        action              TEXT,              -- semi-auto | bolt | lever | etc
        finish              TEXT,
        last_cleaned        TEXT,
        round_count         INTEGER DEFAULT 0,
        ca_compliant        INTEGER DEFAULT 1, -- 1=yes 0=no
        modifications       TEXT,              -- JSON list of mods
        storage_location    TEXT,
        purchase_price      REAL,
        current_value       REAL
    );

    -- ── Gear / clothing ───────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS gear (
        inventory_id        INTEGER PRIMARY KEY REFERENCES inventory(id),
        category            TEXT,              -- jacket | base_layer | pack | etc
        size                TEXT,
        color               TEXT,
        material            TEXT,
        weather_rating      TEXT,              -- rain | wind | cold | etc
        use_case            TEXT,              -- hiking | urban | travel | etc
        wear_count          INTEGER DEFAULT 0,
        last_worn           TEXT
    );

    -- ── Sessions / episodic memory ────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS sessions (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        started_at  TEXT DEFAULT (datetime('now')),
        ended_at    TEXT,
        summary     TEXT,
        topics      TEXT,                      -- comma-separated topics discussed
        mode        TEXT DEFAULT 'chat'        -- chat | interview | research
    );

    -- ── Preferences ───────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS preferences (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        domain          TEXT NOT NULL,
        preference_type TEXT NOT NULL,         -- brand | style | avoid | price_range etc
        value           TEXT NOT NULL,
        strength        INTEGER DEFAULT 5,     -- 1-10
        notes           TEXT,
        created_at      TEXT DEFAULT (datetime('now'))
    );

    -- ── Research history ──────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS research (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        query       TEXT NOT NULL,
        result      TEXT,
        domain      TEXT,
        acted_on    INTEGER DEFAULT 0,         -- did Kenny buy/use this?
        created_at  TEXT DEFAULT (datetime('now'))
    );

    """)
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init_db()
