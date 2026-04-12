# K — Windows Setup

Everything that was running on the Mac mini, now on the Windows rig.

**Target:** RTX 5070 Ti build at `192.168.1.24`
**Prerequisite:** KLLM must be running (`docker compose --profile api up kllm-api` in `C:\kllm`)

---

## What Moves Over from the Mac Mini

| Mac Mini | Windows Rig |
|----------|-------------|
| Qdrant vector DB (Docker) | Same — Docker already installed via KLLM setup |
| Python 3.11 + K venv | `winget` + `python -m venv` |
| Whisper voice input | Same packages, Windows audio driver |
| `k` alias in shell | Git Bash `~/.bashrc` alias |
| `.env` config | Updated with local IPs (no remote rig needed — we are the rig) |

---

## Setup Steps

### 1. Clone the repo

```bash
cd /c
git clone https://github.com/acr79/K.git
cd K
```

### 2. Python 3.11

Check if already installed:

```bash
python --version
```

If not, install via winget (run in PowerShell as Admin):

```powershell
winget install --id Python.Python.3.11 --accept-source-agreements --accept-package-agreements
```

Then restart your terminal.

### 3. Create virtual environment and install deps

```bash
cd /c/K
python -m venv .venv
source .venv/Scripts/activate    # Git Bash
pip install --upgrade pip
pip install -r requirements.txt

# Voice support (Whisper)
pip install openai-whisper sounddevice soundfile numpy
```

> **Note:** `sounddevice` on Windows requires the Visual C++ Redistributable.
> If it fails, download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

### 4. Start Qdrant

Docker Desktop is already installed and runs at boot (via KLLM startup).
Just bring up Qdrant:

```bash
cd /c/K
docker compose up -d qdrant
```

Verify: http://localhost:6333

### 5. Configure .env

```bash
cp .env.example .env
```

Edit `.env`:

```env
# KLLM is running locally — point straight to it
KLLM_BASE_URL=http://localhost:8080/v1
KLLM_MODEL=llama3-8b

# Qdrant running in Docker
QDRANT_URL=http://localhost:6333

# Wake-on-LAN — not needed (we ARE the rig)
# RIG_MAC_ADDRESS=
# RIG_IP=

# Voice — enable once audio is confirmed working
VOICE_ENABLED=false
WHISPER_MODEL=base.en
```

### 6. Add `k` alias to Git Bash

```bash
echo "" >> ~/.bashrc
echo "# K — personal AI" >> ~/.bashrc
echo "alias k='source /c/K/.venv/Scripts/activate && python /c/K/k.py'" >> ~/.bashrc
source ~/.bashrc
```

### 7. Initialize K and run your interview

```bash
source .venv/Scripts/activate
python k.py init
python k.py interview
```

Or once the alias is set:

```bash
k init
k interview
```

---

## Auto-Start Qdrant at Boot

The `C:\kllm\scripts\start-all.ps1` script already starts Docker Desktop at login.
Add Qdrant to it so it comes up automatically:

```powershell
# Add to C:\kllm\scripts\start-all.ps1 after Docker Desktop section:
Write-Host "[..] Starting Qdrant..."
docker compose -f C:\K\docker-compose.yml up -d qdrant
Write-Host "[OK] Qdrant running at http://localhost:6333"
```

Or start it manually after boot:

```bash
cd /c/K && docker compose up -d qdrant
```

---

## Start KLLM API Server

K talks to KLLM over HTTP. Start the API server:

```bash
cd /c/kllm
docker compose --profile api up kllm-api
```

This exposes `http://localhost:8080/v1` — which matches `KLLM_BASE_URL` in your `.env`.

---

## Verify Everything

```bash
# Qdrant up?
curl http://localhost:6333

# KLLM API up?
curl http://localhost:8080/v1/models

# K working?
k chat
```

---

## Access Points

| Service | URL |
|---------|-----|
| KLLM API | http://192.168.1.24:8080/v1 |
| Qdrant | http://192.168.1.24:6333 |
| Ollama | http://192.168.1.24:11434 |
| SSH | `ssh kmoy@kllm.lan` |
| Remote VS Code | `code --remote ssh-remote+kmoy@kllm.lan C:/K` |
