#!/usr/bin/env bash
# K — Mac Mini setup script
# Run once on any Mac to get K fully operational
# Usage: bash scripts/setup-mac.sh

set -e

echo ""
echo "╔══════════════════════════════════╗"
echo "║   K — Mac Setup                 ║"
echo "╚══════════════════════════════════╝"
echo ""

# ── 1. Homebrew ───────────────────────────────────────────────────────────────
if ! command -v brew &>/dev/null; then
  echo "[1/6] Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
  echo "[1/6] Homebrew: OK"
fi

# ── 2. Python 3.11 ───────────────────────────────────────────────────────────
if ! command -v python3.11 &>/dev/null; then
  echo "[2/6] Installing Python 3.11..."
  brew install python@3.11
else
  echo "[2/6] Python: $(python3.11 --version)"
fi

# ── 3. Docker Desktop ────────────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
  echo "[3/6] Installing Docker Desktop..."
  brew install --cask docker
  echo "      Open Docker Desktop once to finish setup, then re-run this script."
  open -a Docker
  exit 0
else
  echo "[3/6] Docker: $(docker --version)"
fi

if ! docker info &>/dev/null; then
  echo "      Docker not running — opening Docker Desktop..."
  open -a Docker
  echo "      Wait for Docker to start, then re-run this script."
  exit 1
fi

# ── 4. Qdrant (vector DB) ────────────────────────────────────────────────────
echo "[4/6] Starting Qdrant..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

docker compose -f "$PROJECT_DIR/docker-compose.yml" up -d qdrant
echo "      Qdrant running at http://localhost:6333"

# ── 5. Python environment ────────────────────────────────────────────────────
echo "[5/6] Setting up Python environment..."
cd "$PROJECT_DIR"

if [[ ! -d ".venv" ]]; then
  python3.11 -m venv .venv
fi

source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Install voice deps
echo "      Installing voice dependencies (Whisper)..."
pip install --quiet openai-whisper sounddevice soundfile numpy

echo "      Python environment ready."

# ── 6. Configure .env ────────────────────────────────────────────────────────
echo "[6/6] Configuring..."
if [[ ! -f "$PROJECT_DIR/.env" ]]; then
  cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
  echo "      Created .env — edit it to set RIG_IP and RIG_MAC_ADDRESS when rig is built."
fi

# Activate venv in shell profile if not already there
SHELL_RC="$HOME/.zshrc"
[[ -f "$HOME/.bashrc" ]] && SHELL_RC="$HOME/.bashrc"

if ! grep -q "K_VENV" "$SHELL_RC" 2>/dev/null; then
  echo "" >> "$SHELL_RC"
  echo "# K — personal AI" >> "$SHELL_RC"
  echo "alias k='source $PROJECT_DIR/.venv/bin/activate && python $PROJECT_DIR/k.py'" >> "$SHELL_RC"
  echo "      Added 'k' alias to $SHELL_RC"
fi

echo ""
echo "╔══════════════════════════════════╗"
echo "║   Setup complete                ║"
echo "╚══════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "  1. Initialize K:"
echo "     source .venv/bin/activate"
echo "     python k.py init"
echo ""
echo "  2. Run your interview (seeds your profile):"
echo "     python k.py interview"
echo ""
echo "  3. Import your gun collection:"
echo "     python k.py import guns /path/to/guns.csv"
echo ""
echo "  4. Start chatting:"
echo "     python k.py chat"
echo ""
echo "  Or after restarting your terminal, just type:"
echo "     k chat"
echo ""
echo "  When your Windows rig is built, edit .env and set:"
echo "     KLLM_BASE_URL=http://<rig-ip>:8080/v1"
echo "     RIG_MAC_ADDRESS=<nic-mac-address>"
echo "     RIG_IP=<rig-ip>"
echo ""
