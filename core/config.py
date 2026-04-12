"""K configuration — local defaults, cloud-swappable."""

import os
import subprocess
from pathlib import Path

# ── SOPS secrets loader ───────────────────────────────────────────────────────
# If secrets.enc.yaml exists, decrypt it and inject into os.environ before
# anything else reads from it.
def _load_sops_secrets():
    secrets_file = Path(__file__).parent.parent / "secrets.enc.yaml"
    if not secrets_file.exists():
        return
    try:
        result = subprocess.run(
            ["sops", "decrypt", "--output-type", "dotenv", str(secrets_file)],
            capture_output=True, text=True, check=True,
            env={**os.environ, "SOPS_AGE_KEY_FILE": str(
                Path.home() / ".config/sops/age/keys.txt"
            )},
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip().strip('"'))
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass  # sops not available or decryption failed — fall through to .env

_load_sops_secrets()

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
