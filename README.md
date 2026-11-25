# WHATSAPP TRACE X
**PHANTOM TEAM · BY KRRISH · @mahisec_13**

A local-first evidence organizer for WhatsApp chat exports and supporting files. It offers two interfaces over the same local case database.

## Two modes

### 1) Desktop mode — local web dashboard
```bash
./start.sh
# Choose 1
```
Open `http://127.0.0.1:5000` on the same device.

### 2) Terminal mode — menu-driven CLI
```bash
./start.sh
# Choose 2
```
All case operations are available from the terminal menu: create/list/view cases, add evidence, inspect preliminary chat indicators, verify SHA-256 hashes, and export PDF/JSON reports.

## Install

Linux / Kali:
```bash
sudo apt update
sudo apt install -y python3 python3-venv
chmod +x start.sh run.sh
./start.sh
```

Android Termux (F-Droid):
```bash
pkg update
pkg install python
chmod +x start.sh
./start.sh
```
If `venv` support is unavailable in your Termux build, install dependencies with `pip install -r requirements.txt` in a supported Python environment and run `python app.py` or `python terminal.py` directly.

## Evidence and reports
- Supports TXT, PDF, PNG, JPG and JPEG files up to 10 MB.
- TXT WhatsApp exports are parsed for preliminary threat/coercion/money-demand indicators; these are review prompts, not proof.
- Other file types are stored locally and hashed, but their contents are not automatically analyzed.
- PDF/JSON reports contain case details, evidence metadata and hashes; original evidence is not embedded.
- SHA-256 verification detects whether a stored file differs from its recorded hash. It does not prove who created it or authenticate its contents.

## Privacy and limitations
- Dashboard binds only to `127.0.0.1`; evidence remains on the device in this local-first build.
- No WhatsApp account/server access, IP lookup, identity discovery, location tracking, password access, or account intrusion.
- Use only chats/files that you own or have permission to review. Keep personal data private and preserve originals.
- Automated flags can be wrong or incomplete. Review full context; this is not a legal finding.
