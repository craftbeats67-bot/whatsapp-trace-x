# WhatsApp Trace X — PHANTOM TEAM

A local-only evidence organizer for documenting suspected blackmail. Includes a Flask desktop dashboard and an interactive terminal menu. It does not access WhatsApp accounts, retrieve private identities, trace IP addresses, locate people, or contact phone numbers.

## Features
- Create investigation cases with an optional country calling code and user-supplied number.
- Structural phone-number format check (not ownership, activity, or WhatsApp verification).
- Import TXT/PDF/PNG/JPG/JPEG/WEBP evidence (10 MB maximum); TXT receives preliminary keyword review; every file gets a SHA-256 hash.
- Add investigator timeline notes.
- Inspect invitation message URLs as text only; links are never opened or downloaded.
- Verify stored evidence hashes.
- Generate PDF case reports.
- Desktop and terminal modes share one local SQLite database.

## Android Termux / Linux / Kali
```bash
pkg update -y
pkg install python -y
# Extract the ZIP, enter the project directory:
chmod +x start.sh
./start.sh
```
The launcher creates a virtual environment where supported and installs dependencies. On first run it needs internet access to install Flask and ReportLab.

## Desktop mode
Choose `1` in the launcher, then open `http://127.0.0.1:5000` on the same device.

## Terminal mode
Choose `2`. Menu options include create/list/view case, add evidence, add notes, verify SHA-256, generate PDF, validate a phone format, and inspect pasted invitation text.

## PDF location
`reports/case_<CASE_ID>_report.pdf`

## Privacy and limitations
- Keep this project local. Do not expose the dashboard to the public internet.
- Do not upload private chats, screenshots, database files, evidence, passwords, tokens, or `.env` files to GitHub.
- Keyword hits are only review prompts and may produce false positives/negatives. They do not prove blackmail.
- Phone checks are formatting-only. The tool cannot identify the owner or location of a number.
- URL inspection is static text parsing only; it does not visit links, resolve redirects, join groups, or download content.
- Preserve originals and share evidence with the appropriate authorities. Do not confront or threaten a suspect.

## Project checks
```bash
python -m py_compile core.py app.py terminal.py
python -m unittest discover -s tests -v
```
