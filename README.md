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
WHATSAPP TRACE X — PHANTOM TEAM

Digital Evidence & Blackmail Investigation Support Tool

A local evidence-management application featuring a Flask desktop dashboard and an interactive PHANTOM TEAM terminal interface.

The project helps users organize supplied evidence related to suspected online blackmail, preserve file integrity, review exported WhatsApp conversations and generate investigation reports.

---

1. Main Features

- Desktop Dashboard using Flask
- Professional PHANTOM TEAM Terminal Mode
- Investigation case creation and management
- Country calling code and phone-number format validation
- WhatsApp TXT export keyword analysis
- Evidence import: TXT, PDF, PNG, JPG, JPEG and WEBP
- SHA-256 evidence hashing and verification
- Investigation timeline notes
- Invitation message and URL text inspection
- PDF investigation report generation
- JSON report support, where implemented
- Local SQLite database

2. Terminal Mode — Detailed Guide

Start the terminal interface:

python terminal.py

The terminal interface provides the following modules.

[01] Create Case

Creates a new investigation record.

Information may include:

- Case title
- Country calling code
- User-supplied phone number
- Investigation description

Example:

Select: 01
Case title: Suspicious WhatsApp Blackmail
Country code: +91
Phone number: Enter the supplied number

The phone number is stored as supplied investigation information. Format validation does not identify its owner.

[02] Case Register

Displays previously created investigation cases.

Use this option to review available case records and their IDs.

[03] View Case

Displays information associated with a selected case.

This may include case details, evidence records and investigation notes.

[04] Add Evidence

Adds user-provided evidence files to a case.

Supported formats:

- TXT
- PDF
- PNG
- JPG / JPEG
- WEBP

The application calculates a SHA-256 hash for stored evidence.

TXT files receive preliminary keyword-based review. Other formats are stored and hashed; their contents are not automatically interpreted unless a separate extraction feature is implemented.

[05] Add Timeline Note

Adds a dated investigation note.

Example:

Date: 2026-11-26
Note: Victim supplied a WhatsApp conversation export.

Keep notes factual and distinguish reported claims from independently verified information.

[06] Verify Evidence Hash

Checks whether a stored evidence file still matches its recorded SHA-256 hash.

A matching hash supports file-integrity checking. It does not independently prove that the original evidence is authentic.

[07] Generate PDF Report

Generates a case report containing available case details, evidence records, hashes and notes.

Expected report location:

reports/case_<CASE_ID>_report.pdf

Example:

reports/case_1_report.pdf

[08] Inspect Phone Format

Checks the basic structure of a supplied phone number and country calling code.

It does not:

- Identify the private owner
- Verify WhatsApp registration
- Reveal IP addresses
- Retrieve a person's location

[09] Inspect Invitation Text / Link

Inspects invitation message or URL text supplied by the user.

The tool can identify URL hosts and configured suspicious text patterns.

It does not open links, join groups, download content or verify private group membership.

[00] Exit

Closes the terminal interface.

---

3. Installation — Android Termux

Install required packages:

pkg update -y
pkg install python git unzip -y
termux-setup-storage

Extract the downloaded project ZIP and enter its directory.

Install project dependencies:

python -m pip install -r requirements.txt

Start the application:

chmod +x start.sh
./start.sh

Select the desired mode from the launcher.

4. Installation — Kali Linux / Linux

sudo apt update
sudo apt install python3 python3-venv python3-pip git unzip -y

Enter the project directory:

cd whatsapp-trace-x

Create a virtual environment:

python3 -m venv .venv
source .venv/bin/activate

Install dependencies:

python -m pip install -r requirements.txt

Start the launcher:

chmod +x start.sh
./start.sh

5. Desktop Dashboard

Select Desktop Mode in the launcher.

Open the local dashboard on the same device:

http://127.0.0.1:5000

Do not expose the local dashboard to the public internet.

6. Project Checks

Check Python syntax:

python -m py_compile core.py app.py terminal.py

Run automated tests:

python -m unittest discover -s tests -v

These commands check syntax and available automated tests. They do not guarantee that every device, dependency or feature works in every environment.

7. Troubleshooting

ModuleNotFoundError

Install the dependencies:

python -m pip install -r requirements.txt

Permission denied

chmod +x start.sh

PDF report not found

Check the reports directory:

ls -lh reports/

Terminal interface does not start

python -m py_compile terminal.py
python terminal.py

GitHub authentication failed

Use your GitHub username and an appropriate Personal Access Token. Never publish the token.

8. Privacy and Responsible Use

- Keep investigations local and secure.
- Never publish private chats, screenshots, evidence files, databases or credentials.
- Preserve original evidence files.
- Do not access accounts or devices without authorization.
- Do not secretly track or identify private individuals.
- Keyword matches are preliminary indicators, not proof of blackmail.
- Preserve relevant evidence and report suspected crimes to the appropriate authorities.

India's National Cyber Crime Reporting Portal:

https://cybercrime.gov.in/

9. Limitations

WhatsApp Trace X is an evidence-management tool, not an automatic identity-tracing or account-access tool.

It cannot independently identify a suspect, retrieve private WhatsApp information, trace a live location or establish guilt.

10. Credits

Project: WhatsApp Trace X
Team: PHANTOM TEAM
Interface: Desktop Dashboard + Terminal Mode
Purpose: Digital Evidence Organization and Investigation Support
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
