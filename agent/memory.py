"""Memory retrieval — pulls relevant context for any query."""

from ..core.vector_store import retrieve_all
from ..core.database import get_conn
from ..core.config import MAX_CONTEXT_FACTS


def get_context(query: str) -> str:
    """Build a context block to inject into the LLM prompt."""
    facts = retrieve_all(query, limit=MAX_CONTEXT_FACTS)

    if not facts:
        return ""

    lines = ["=== What K knows about Kenny (relevant to this query) ==="]
    for f in facts:
        lines.append(f"• {f['text']}")

    return "\n".join(lines)


def get_inventory_context(domain: str = None) -> str:
    """Pull structured inventory summary."""
    conn = get_conn()

    if domain:
        rows = conn.execute(
            "SELECT domain, name, brand, model, notes FROM inventory WHERE domain=? ORDER BY domain, name",
            (domain,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT domain, name, brand, model, notes FROM inventory ORDER BY domain, name"
        ).fetchall()

    conn.close()

    if not rows:
        return ""

    lines = ["=== Kenny's Inventory ==="]
    current_domain = None
    for row in rows:
        if row["domain"] != current_domain:
            lines.append(f"\n{row['domain'].upper()}:")
            current_domain = row["domain"]
        entry = f"  • {row['name']}"
        if row["brand"]:
            entry += f" ({row['brand']}"
            if row["model"]:
                entry += f" {row['model']}"
            entry += ")"
        if row["notes"]:
            entry += f" — {row['notes']}"
        lines.append(entry)

    return "\n".join(lines)


def save_episode(summary: str, topics: list[str]):
    """Save a conversation episode to episodic memory."""
    from ..core.vector_store import store_fact
    from ..core.config import COLLECTION_EPISODES

    conn = get_conn()
    conn.execute(
        "INSERT INTO sessions (summary, topics, ended_at) VALUES (?, ?, datetime('now'))",
        (summary, ",".join(topics))
    )
    conn.commit()
    conn.close()

    store_fact(
        text=summary,
        metadata={"type": "episode", "topics": topics},
        collection=COLLECTION_EPISODES
    )
