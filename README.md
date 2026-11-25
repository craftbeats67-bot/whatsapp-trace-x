# WHATSAPP TRACE X
**PHANTOM TEAM · BY KRRISH · @mahisec_13**

A local-first digital evidence organizer for WhatsApp blackmail/harassment reports.

## Features
- Create local incident cases.
- Import WhatsApp `.txt` chat exports.
- Parse common WhatsApp export timestamp formats.
- Flag possible threat, money-demand, and coercion language for human review.
- Upload supporting TXT, PNG, JPG, JPEG, and PDF evidence (max 10 MB each).
- Calculate SHA-256 hashes and verify whether stored evidence changed.
- Download a generated PDF case report with case details, evidence register, SHA-256 hashes, and preliminary indicators.
- Export a JSON case report.
- Terminal CLI analyzer.

## Kali Linux installation
```bash
sudo apt update
sudo apt install -y python3 python3-venv
chmod +x run.sh
./run.sh
```
Open `http://127.0.0.1:5000` on the same laptop.

## PDF report
Open a case and tap **Download PDF report**. The PDF is generated locally when requested; original evidence files are not embedded in the report. Install dependencies with `pip install -r requirements.txt` to enable PDF export.

## CLI usage
```bash
source .venv/bin/activate
python cli.py /path/to/WhatsApp_Chat.txt --json report.json
```

## How to export a WhatsApp chat
In WhatsApp, open the relevant chat, use the chat menu and choose **Export chat**. Prefer **without media** for the TXT analysis. Only import chats the victim has chosen to provide and is authorized to share.

## Important limitations
- This tool does not access WhatsApp servers, private accounts, phone locations, IP addresses, passwords, or message databases.
- A phone number format check does not prove who owns that number.
- Keyword flags are only clues. They can produce false positives and miss context, sarcasm, other languages, or spelling variations.
- The tool cannot authenticate screenshots or prove who sent a message.
- Keep the original WhatsApp export and device intact. Do not edit original evidence.
- Reports are organizational aids, not legal findings.

## Privacy
The app binds only to `127.0.0.1` and does not upload evidence to a cloud service. Keep the project folder private, use full-disk encryption, and do not share reports containing personal information except with the victim, trusted support, or appropriate authorities.

## Branding
PHANTOM TEAM · BY KRRISH · Instagram: @mahisec_13
