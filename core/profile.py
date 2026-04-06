"""Profile management — read/write Kenny's structured profile."""

from .database import get_conn
from .vector_store import store_fact
from .config import COLLECTION_MEMORY


def set_fact(key: str, value: str, domain: str = "general", source: str = "interview"):
    """Store a structured profile fact."""
    conn = get_conn()
    conn.execute("""
        INSERT INTO profile (key, value, domain, source, updated_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        ON CONFLICT(key) DO UPDATE SET
            value=excluded.value,
            domain=excluded.domain,
            source=excluded.source,
            updated_at=datetime('now')
    """, (key, value, domain, source))
    conn.commit()
    conn.close()

    # Also store semantically
    store_fact(
        text=f"{key}: {value}",
        metadata={"type": "profile", "key": key, "domain": domain, "source": source}
    )


def get_fact(key: str) -> str | None:
    conn = get_conn()
    row = conn.execute("SELECT value FROM profile WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else None


def get_all_facts(domain: str = None) -> list[dict]:
    conn = get_conn()
    if domain:
        rows = conn.execute(
            "SELECT * FROM profile WHERE domain=? ORDER BY domain, key", (domain,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM profile ORDER BY domain, key").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def set_domain_expertise(domain: str, level: str, interest: int = 5, notes: str = None):
    """Set expertise level for a domain."""
    conn = get_conn()
    conn.execute("""
        INSERT INTO domains (name, expertise_level, interest_level, notes, updated_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        ON CONFLICT(name) DO UPDATE SET
            expertise_level=excluded.expertise_level,
            interest_level=excluded.interest_level,
            notes=excluded.notes,
            updated_at=datetime('now')
    """, (domain, level, interest, notes))
    conn.commit()
    conn.close()

    store_fact(
        text=f"Kenny's expertise in {domain}: {level} (interest: {interest}/10). {notes or ''}",
        metadata={"type": "expertise", "domain": domain, "level": level}
    )


def get_domain_expertise(domain: str) -> dict | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM domains WHERE name=?", (domain,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_preference(domain: str, preference_type: str, value: str,
                   strength: int = 5, notes: str = None):
    conn = get_conn()
    conn.execute("""
        INSERT INTO preferences (domain, preference_type, value, strength, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (domain, preference_type, value, strength, notes))
    conn.commit()
    conn.close()

    store_fact(
        text=f"Kenny preference in {domain} — {preference_type}: {value}. {notes or ''}",
        metadata={"type": "preference", "domain": domain,
                  "preference_type": preference_type, "strength": strength}
    )


def print_profile_summary():
    facts = get_all_facts()
    conn = get_conn()
    domains = conn.execute("SELECT * FROM domains ORDER BY interest_level DESC").fetchall()
    prefs = conn.execute("SELECT * FROM preferences ORDER BY domain, strength DESC").fetchall()
    conn.close()

    print("\n=== K Profile Summary ===\n")
    print("── Core Facts ──")
    for f in facts:
        print(f"  {f['key']}: {f['value']}")

    print("\n── Domain Expertise ──")
    for d in domains:
        print(f"  {d['name']}: {d['expertise_level']} (interest {d['interest_level']}/10)")

    print("\n── Preferences ──")
    current_domain = None
    for p in prefs:
        if p['domain'] != current_domain:
            print(f"  {p['domain']}:")
            current_domain = p['domain']
        print(f"    {p['preference_type']}: {p['value']} [{p['strength']}/10]")
