"""K configuration — local defaults, cloud-swappable."""

import os
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
K_HOME = Path(os.environ.get("K_HOME", Path.home() / ".k"))
K_HOME.mkdir(parents=True, exist_ok=True)

DB_PATH = Path(os.environ.get("K_DB", K_HOME / "k.db"))

# ── KLLM inference endpoint ───────────────────────────────────────────────────
# Points to local Docker when rig is on same machine, or rig IP on LAN
KLLM_BASE_URL = os.environ.get("KLLM_BASE_URL", "http://localhost:8080/v1")
KLLM_MODEL    = os.environ.get("KLLM_MODEL", "llama3-8b")
KLLM_API_KEY  = os.environ.get("KLLM_API_KEY", "none")  # no auth on local network

# ── Vector store (Qdrant) ─────────────────────────────────────────────────────
# Local Docker by default → swap QDRANT_URL to cloud when ready
QDRANT_URL    = os.environ.get("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", None)

# Collection names
COLLECTION_MEMORY    = "k_memory"     # semantic facts about Kenny
COLLECTION_INVENTORY = "k_inventory"  # searchable inventory
COLLECTION_EPISODES  = "k_episodes"   # past conversation summaries

# ── Embedding model (runs locally on Mac) ────────────────────────────────────
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIM   = 384  # matches all-MiniLM-L6-v2

# ── Wake-on-LAN ───────────────────────────────────────────────────────────────
# Fill these in when the Windows rig is built
RIG_MAC_ADDRESS = os.environ.get("RIG_MAC_ADDRESS", "")   # e.g. "AA:BB:CC:DD:EE:FF"
RIG_IP          = os.environ.get("RIG_IP", "")            # e.g. "192.168.1.100"
RIG_BOOT_WAIT   = int(os.environ.get("RIG_BOOT_WAIT", "90"))  # seconds to wait after WoL

# ── Voice ─────────────────────────────────────────────────────────────────────
WHISPER_MODEL   = os.environ.get("WHISPER_MODEL", "base.en")  # tiny/base/small/medium
VOICE_ENABLED   = os.environ.get("VOICE_ENABLED", "false").lower() == "true"

# ── Response tuning ───────────────────────────────────────────────────────────
MAX_CONTEXT_FACTS = 10    # how many memory facts to inject per query
MAX_TOKENS        = 1024
STREAM_RESPONSES  = True
