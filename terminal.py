#!/usr/bin/env python3
"""Interactive terminal interface for WhatsApp Trace X (local evidence organizer)."""
from pathlib import Path
import hashlib, sqlite3, sys
from app import app, init_db, db, EVIDENCE, now, sha256_file
from analyzer import parse_chat, analyze_messages
from werkzeug.utils import secure_filename

MAX_BYTES = 10 * 1024 * 1024
ALLOWED = {'.txt', '.pdf', '.png', '.jpg', '.jpeg'}

def pause():
    input('\nEnter dabao menu par lautne ke liye...')

def cases():
    with db() as con:
        return con.execute('SELECT * FROM cases ORDER BY id DESC').fetchall()

def choose_case():
    rows = cases()
    if not rows:
        print('\nAbhi koi case nahi hai. Pehle case banao.')
        return None
    print('\nCases:')
    for c in rows:
        print(f"  #{c['id']}  {c['title']}  ({c['created_at']})")
    try:
        cid = int(input('Case ID: ').strip())
    except ValueError:
        print('Invalid ID.'); return None
    with db() as con:
        row = con.execute('SELECT * FROM cases WHERE id=?', (cid,)).fetchone()
    if not row: print('Case nahi mila.')
    return row

def create_case():
    title = input('Case title: ').strip()
    if not title or len(title) > 120:
        print('Title required hai (maximum 120 characters).'); return
    phone = input('Contact/phone reference (optional): ').strip()[:40]
    notes = input('Notes (optional): ').strip()[:2000]
    with db() as con:
        cur = con.execute('INSERT INTO cases(title,phone,notes,created_at) VALUES(?,?,?,?)', (title, phone, notes, now()))
        con.commit()
    print(f'Case #{cur.lastrowid} create ho gaya.')

def add_evidence():
    case = choose_case()
    if not case: return
    raw_path = input('Evidence file ka full path (TXT/PDF/JPG/PNG): ').strip().strip('"').strip("'")
    path = Path(raw_path).expanduser()
    if not path.is_file(): print('File nahi mili.'); return
    ext = path.suffix.lower()
    if ext not in ALLOWED: print('Unsupported file type.'); return
    if path.stat().st_size > MAX_BYTES: print('Maximum file size 10 MB hai.'); return
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    stored = f"case{case['id']}_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{ext}"
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / stored).write_bytes(data)
    kind = 'WhatsApp chat export' if ext == '.txt' else 'Supporting attachment'
    with db() as con:
        cur = con.execute('INSERT INTO evidence(case_id,original_name,stored_name,sha256,size,kind,added_at) VALUES(?,?,?,?,?,?,?)',
                          (case['id'], secure_filename(path.name), stored, digest, len(data), kind, now()))
        eid = cur.lastrowid
        con.commit()
    print(f'Evidence #{eid} saved. SHA-256: {digest}')
    if ext == '.txt':
        messages = parse_chat(data.decode('utf-8-sig', errors='replace'))
        findings = analyze_messages(messages)
        with db() as con:
            for item in findings:
                con.execute('INSERT INTO findings(case_id,source_evidence_id,message_time,message,category) VALUES(?,?,?,?,?)',
                            (case['id'], eid, item['time'], item['message'], item['category']))
            con.commit()
        print(f'{len(messages)} messages parse hue; {len(findings)} possible indicators human review ke liye.')
    else:
        print('File store hui; non-TXT file ka content automatically analyze nahi hota.')

def show_case():
    case = choose_case()
    if not case: return
    with db() as con:
        ev = con.execute('SELECT * FROM evidence WHERE case_id=? ORDER BY id', (case['id'],)).fetchall()
        findings = con.execute('SELECT * FROM findings WHERE case_id=? ORDER BY id', (case['id'],)).fetchall()
    print(f"\nCASE #{case['id']}: {case['title']}\nCreated: {case['created_at']}\nContact: {case['phone'] or 'Not recorded'}\nNotes: {case['notes'] or 'None'}")
    print('\nEvidence:')
    for x in ev: print(f"  [{x['id']}] {x['original_name']} | {x['size']} bytes | SHA256 {x['sha256']}")
    print('\nPossible indicators (preliminary, verify context):')
    for x in findings: print(f"  [{x['category']}] {x['message_time']} :: {x['message']}")
    if not findings: print('  None flagged (does not prove no incident occurred).')

def verify_case():
    case = choose_case()
    if not case: return
    with db() as con: rows = con.execute('SELECT * FROM evidence WHERE case_id=?', (case['id'],)).fetchall()
    if not rows: print('Is case mein evidence nahi hai.'); return
    for x in rows:
        p = EVIDENCE / x['stored_name']
        actual = sha256_file(p) if p.exists() else 'MISSING'
        print(f"{'MATCH' if actual == x['sha256'] else 'MISMATCH/MISSING'} | {x['original_name']}")

def export_report(pdf=False):
    case = choose_case()
    if not case: return
    endpoint = f"/case/{case['id']}/report.pdf" if pdf else f"/case/{case['id']}/report"
    with app.test_client() as client:
        response = client.get(endpoint)
    if response.status_code != 200:
        print(f'Report generate nahi hui (HTTP {response.status_code}). PDF ke liye dependencies install karo.'); return
    outdir = Path('reports'); outdir.mkdir(exist_ok=True)
    ext = 'pdf' if pdf else 'json'
    out = outdir / f"case_{case['id']}_report.{ext}"
    out.write_bytes(response.data)
    print(f'Report save ho gayi: {out.resolve()}')

def main():
    init_db()
    while True:
        print('\n' + '='*48)
        print(' WHATSAPP TRACE X | PHANTOM TEAM')
        print(' BY KRRISH | @mahisec_13 | TERMINAL MODE')
        print('='*48)
        print('1. Create new case')
        print('2. List cases')
        print('3. View case and analysis')
        print('4. Add evidence file')
        print('5. Verify evidence SHA-256')
        print('6. Export case report (PDF)')
        print('7. Export case report (JSON)')
        print('0. Exit')
        choice = input('\nOption select karo: ').strip()
        if choice == '1': create_case(); pause()
        elif choice == '2':
            rows = cases()
            for c in rows: print(f"#{c['id']} | {c['title']} | {c['created_at']}")
            if not rows: print('No cases yet.')
            pause()
        elif choice == '3': show_case(); pause()
        elif choice == '4': add_evidence(); pause()
        elif choice == '5': verify_case(); pause()
        elif choice == '6': export_report(True); pause()
        elif choice == '7': export_report(False); pause()
        elif choice == '0': print('WhatsApp Trace X closed.'); break
        else: print('Invalid option.'); pause()

if __name__ == '__main__':
    try: main()
    except (KeyboardInterrupt, EOFError): print('\nExited safely.'); sys.exit(0)
