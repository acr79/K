"""Import inventory from spreadsheets — guns first, extensible to anything."""

import csv
from pathlib import Path
from ..core.database import get_conn
from ..core.vector_store import store_fact
from ..core.config import COLLECTION_INVENTORY


# Map your spreadsheet column names → our schema
# Edit these to match your actual spreadsheet headers
GUN_COLUMN_MAP = {
    "serial":           "serial_number",
    "serial_number":    "serial_number",
    "serial number":    "serial_number",
    "type":             "type",
    "gun_type":         "type",
    "manufacturer":     "manufacturer",
    "make":             "manufacturer",
    "model":            "model",
    "caliber":          "caliber",
    "cal":              "caliber",
    "name":             "name",
    "notes":            "notes",
    "purchase_price":   "purchase_price",
    "price":            "purchase_price",
    "value":            "current_value",
    "location":         "storage_location",
    "storage":          "storage_location",
    "ca_compliant":     "ca_compliant",
    "compliant":        "ca_compliant",
    "last_cleaned":     "last_cleaned",
    "round_count":      "round_count",
    "rounds":           "round_count",
    "mods":             "modifications",
    "modifications":    "modifications",
}


def import_guns_csv(filepath: str, dry_run: bool = False) -> int:
    """
    Import guns from a CSV file. Returns number of records imported.
    Set dry_run=True to preview without writing.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    conn = get_conn()
    imported = 0
    skipped = 0

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Normalize column names
            normalized = {}
            for col, val in row.items():
                key = GUN_COLUMN_MAP.get(col.lower().strip().replace(" ", "_"), None)
                if key and val and val.strip():
                    normalized[key] = val.strip()

            serial = normalized.get("serial_number")
            if not serial:
                print(f"  Skipping row — no serial number: {dict(row)}")
                skipped += 1
                continue

            # Build display name
            name_parts = [
                normalized.get("manufacturer", ""),
                normalized.get("model", ""),
                normalized.get("caliber", ""),
            ]
            name = " ".join(p for p in name_parts if p) or f"Gun {serial}"

            if dry_run:
                print(f"  Would import: {name} (serial: {serial})")
                imported += 1
                continue

            try:
                # Insert into inventory base table
                cursor = conn.execute("""
                    INSERT OR IGNORE INTO inventory (domain, name, brand, model, notes)
                    VALUES ('guns', ?, ?, ?, ?)
                """, (
                    name,
                    normalized.get("manufacturer"),
                    normalized.get("model"),
                    normalized.get("notes"),
                ))
                inventory_id = cursor.lastrowid

                if inventory_id == 0:
                    # Already exists — get the ID
                    row_exists = conn.execute(
                        "SELECT id FROM inventory WHERE domain='guns' AND name=?", (name,)
                    ).fetchone()
                    if row_exists:
                        inventory_id = row_exists["id"]

                # Insert gun-specific data
                conn.execute("""
                    INSERT OR REPLACE INTO guns
                        (inventory_id, serial_number, type, manufacturer, model,
                         caliber, storage_location, purchase_price, current_value,
                         last_cleaned, round_count, modifications, ca_compliant)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    inventory_id,
                    serial,
                    normalized.get("type"),
                    normalized.get("manufacturer"),
                    normalized.get("model"),
                    normalized.get("caliber"),
                    normalized.get("storage_location"),
                    normalized.get("purchase_price"),
                    normalized.get("current_value"),
                    normalized.get("last_cleaned"),
                    normalized.get("round_count"),
                    normalized.get("modifications"),
                    1 if normalized.get("ca_compliant", "yes").lower()
                         not in ("no", "0", "false") else 0,
                ))

                # Store in vector index for semantic search
                store_fact(
                    text=f"Gun: {name}, serial {serial}, "
                         f"type: {normalized.get('type', 'unknown')}, "
                         f"caliber: {normalized.get('caliber', 'unknown')}. "
                         f"{normalized.get('notes', '')}",
                    metadata={"type": "gun", "serial": serial, "name": name},
                    collection=COLLECTION_INVENTORY
                )

                imported += 1
                print(f"  ✓ {name} ({serial})")

            except Exception as e:
                print(f"  ✗ Error importing {serial}: {e}")
                skipped += 1

    if not dry_run:
        conn.commit()
    conn.close()

    print(f"\nImported: {imported}  Skipped: {skipped}")
    return imported
