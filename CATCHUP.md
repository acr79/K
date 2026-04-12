# K — Catchup

## What This Is
K is your personal AI. It knows you — your gear, guns, preferences, expertise, buying habits.
It runs on the Mac mini (always on, low power) and uses the Windows rig (kllm.lan) for inference.

---

## Current State (as of 2026-04-11)

### Infrastructure — DONE
- **Windows rig** (`kllm.lan` / `192.168.1.41`, user `kmoy`) is fully set up:
  - KLLM API running on port 8080 (Llama 3 8B, GPU-accelerated)
  - Qdrant vector DB on port 6333
  - Ollama on port 11434
  - Auto-starts on boot via Windows Startup folder
- **Mac mini** — K is installed and configured, pointing to the Windows rig

### What Still Needs to Happen
- [ ] **Run the interview** — K has no profile data yet. This is the most important next step:
  ```bash
  cd ~/K
  source .venv/bin/activate
  python k.py interview
  ```
  Takes ~15 min. Seeds your profile, expertise, inventory knowledge, preferences.

- [ ] **Enable Wake-on-LAN on Windows rig** (so Mac mini can wake it from sleep):
  - BIOS: `Settings → Advanced → Power Management → ErP: Disabled, Wake on LAN: Enabled`
  - Windows: Disable Fast Startup (`Power Options → Choose what power buttons do`)
  - Plug Ethernet into the rig (WiFi WoL is unreliable)
  - NIC: Device Manager → Ethernet → Properties → Power Management → Allow magic packet wake

- [ ] **Import inventory** — once interview is done:
  ```bash
  python k.py import guns ~/path/to/guns.csv   # if you have a CSV
  # or just tell K about your guns in chat — it can record them
  ```

---

## Daily Use (once interview is done)

```bash
cd ~/K
source .venv/bin/activate
python k.py chat        # text chat
python k.py voice       # voice mode (mic required, VOICE_ENABLED=true in .env)
```

Or with the alias (after restarting terminal):
```bash
k chat
k voice
```

---

## How Wake-on-LAN Works
When you ask K something, it automatically:
1. Checks if the Windows rig (`192.168.1.41:8080`) is up
2. If not — sends a magic packet to wake it (MAC: `10:FF:E0:B7:30:F6`)
3. Waits up to 120s for the KLLM API to come up
4. Proceeds with your query

Cold boot to first response: ~60–70 seconds.

---

## Key Files
| File | Purpose |
|------|---------|
| `~/.k/k.db` | SQLite — all your profile, inventory, history |
| `.env` | Config — points to Windows rig IP, WoL MAC |
| `scripts/wake.py` | Sends magic packet to wake Windows rig |
| `WINDOWS_SETUP.md` | Full setup guide for the Windows rig |

---

## Access Points
| Service | Address |
|---------|---------|
| KLLM API | http://192.168.1.41:8080/v1 |
| Qdrant (on rig) | http://192.168.1.41:6333 |
| Ollama | http://192.168.1.41:11434 |
| SSH to rig | `ssh kmoy@kllm.lan` |
| Remote VS Code | `code --remote ssh-remote+kmoy@kllm.lan C:/kllm` |
