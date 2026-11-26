"""Local-only evidence organizer for documenting suspected blackmail."""
from __future__ import annotations
import hashlib, json, re, sqlite3, uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
EVIDENCE = DATA / 'evidence'
REPORTS = ROOT / 'reports'
DB = DATA / 'trace_x.db'
ALLOWED = {'.txt', '.pdf', '.png', '.jpg', '.jpeg', '.webp'}
MAX_BYTES = 10 * 1024 * 1024
THREAT_TERMS = [
    'blackmail', 'pay me', 'send money', 'otherwise', 'i will leak', 'leak your',
    'viral', 'expose you', 'delete nahi', 'paise bhejo', 'paisa bhejo',
    'dhamki', 'badnaam', 'share kar dunga', 'share kar dungi', 'bhejo warna',
    'police ko', 'private photo', 'private video'
]
MONEY_RE = re.compile(r'(?:₹|rs\.?\s*|inr\s*)\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?', re.I)

for p in (DATA, EVIDENCE, REPORTS): p.mkdir(parents=True, exist_ok=True)

def connect():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    c.executescript('''
    CREATE TABLE IF NOT EXISTS cases (
      id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, notes TEXT DEFAULT '',
      country_code TEXT DEFAULT '', phone_number TEXT DEFAULT '', created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS evidence (
      id INTEGER PRIMARY KEY AUTOINCREMENT, case_id INTEGER NOT NULL,
      original_name TEXT NOT NULL, stored_name TEXT NOT NULL, sha256 TEXT NOT NULL,
      size_bytes INTEGER NOT NULL, mime_type TEXT DEFAULT '', added_at TEXT NOT NULL,
      analysis_json TEXT DEFAULT '{}', FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS notes (
      id INTEGER PRIMARY KEY AUTOINCREMENT, case_id INTEGER NOT NULL,
      body TEXT NOT NULL, created_at TEXT NOT NULL,
      FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE
    );
    '''); c.commit(); return c

def now(): return datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')
def sha256_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
def validate_phone(country_code, number):
    cc = country_code.strip(); num = number.strip()
    if not re.fullmatch(r'\+[1-9]\d{0,3}', cc): return False, 'Country code must look like +91 or +1.'
    digits = re.sub(r'[\s()-]', '', num)
    if not digits.isdigit() or not 4 <= len(digits) <= 14: return False, 'Enter 4–14 digits only (without country code).'
    # Structural validation only; not proof that a number is assigned or belongs to anyone.
    if digits.startswith('0'): return False, 'Remove the leading trunk zero after the country code.'
    return True, cc + digits

def analyze_text(text):
    lines=text.splitlines(); findings=[]
    for i,line in enumerate(lines,1):
        low=line.casefold(); hits=[t for t in THREAT_TERMS if t in low]
        money=bool(MONEY_RE.search(line))
        if hits or money:
            findings.append({'line':i,'text':line[:1000], 'indicators':hits + (['money-amount-pattern'] if money else [])})
    return {'kind':'text_keyword_review','lines':len(lines),'flagged_lines':findings,
            'notice':'Automated keyword flags are preliminary indicators, not proof of blackmail or identity.'}

def inspect_invitation(text):
    urls=re.findall(r'https?://[^\s<>"\']+', text, flags=re.I)
    results=[]
    for raw in urls[:100]:
        clean=raw.rstrip('.,);]')
        try:
            u=urlparse(clean); host=(u.hostname or '').lower()
            flags=[]
            if u.scheme != 'https': flags.append('not-https')
            if host.startswith('xn--') or '.xn--' in host: flags.append('punycode-host')
            if re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$',host): flags.append('ip-address-host')
            if '@' in u.netloc: flags.append('userinfo-in-url')
            results.append({'url':clean[:500],'host':host,'indicators':flags})
        except Exception: results.append({'url':clean[:500],'host':'','indicators':['unparseable-url']})
    return {'urls':results,'notice':'URLs are inspected as text only. The tool does not open links, join groups, or verify who controls them.'}

def create_case(title, notes='', country_code='', phone_number=''):
    title=title.strip()[:120]
    if not title: raise ValueError('Case title is required.')
    if country_code or phone_number:
        ok, val=validate_phone(country_code,phone_number)
        if not ok: raise ValueError(val)
        phone_number=val
    with connect() as c:
        cur=c.execute('INSERT INTO cases(title,notes,country_code,phone_number,created_at) VALUES(?,?,?,?,?)',
                      (title,notes[:5000],country_code,phone_number,now()))
        return cur.lastrowid

def add_evidence(case_id, source_path, original_name=None, mime_type=''):
    src=Path(source_path)
    if not src.is_file(): raise ValueError('Evidence file not found.')
    ext=src.suffix.lower()
    if ext not in ALLOWED: raise ValueError('Allowed formats: TXT, PDF, PNG, JPG, JPEG, WEBP.')
    size=src.stat().st_size
    if size > MAX_BYTES: raise ValueError('Maximum file size is 10 MB.')
    with connect() as c:
        if not c.execute('SELECT id FROM cases WHERE id=?',(case_id,)).fetchone(): raise ValueError('Case not found.')
        stored=f'{uuid.uuid4().hex}{ext}'; dest=EVIDENCE/stored
        dest.write_bytes(src.read_bytes()); digest=sha256_file(dest)
        analysis={}
        if ext=='.txt':
            try: analysis=analyze_text(dest.read_text(encoding='utf-8-sig',errors='replace'))
            except Exception as e: analysis={'error':str(e)}
        c.execute('INSERT INTO evidence(case_id,original_name,stored_name,sha256,size_bytes,mime_type,added_at,analysis_json) VALUES(?,?,?,?,?,?,?,?)',
                  (case_id,(original_name or src.name)[:255],stored,digest,size,mime_type,now(),json.dumps(analysis,ensure_ascii=False)))
        return c.execute('SELECT last_insert_rowid()').fetchone()[0]

def add_note(case_id, body):
    body=body.strip()
    if not body: raise ValueError('Note cannot be empty.')
    with connect() as c:
        c.execute('INSERT INTO notes(case_id,body,created_at) VALUES(?,?,?)',(case_id,body[:10000],now()))

def get_case(case_id):
    with connect() as c:
        case=c.execute('SELECT * FROM cases WHERE id=?',(case_id,)).fetchone()
        if not case: return None
        evid=c.execute('SELECT * FROM evidence WHERE case_id=? ORDER BY id',(case_id,)).fetchall()
        notes=c.execute('SELECT * FROM notes WHERE case_id=? ORDER BY id',(case_id,)).fetchall()
    return {'case':dict(case),'evidence':[dict(x) for x in evid],'notes':[dict(x) for x in notes]}

def list_cases():
    with connect() as c: return [dict(x) for x in c.execute('SELECT * FROM cases ORDER BY id DESC')]
def verify_evidence(evidence_id):
    with connect() as c: row=c.execute('SELECT * FROM evidence WHERE id=?',(evidence_id,)).fetchone()
    if not row: raise ValueError('Evidence ID not found.')
    path=EVIDENCE/row['stored_name']
    return {'exists':path.is_file(),'matches':path.is_file() and sha256_file(path)==row['sha256'],
            'expected':row['sha256'],'actual':sha256_file(path) if path.is_file() else None}

def build_report(case_id):
    data=get_case(case_id)
    if not data: raise ValueError('Case not found.')
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    out=REPORTS/f'case_{case_id}_report.pdf'
    doc=SimpleDocTemplate(str(out),pagesize=A4,rightMargin=16*mm,leftMargin=16*mm,topMargin=16*mm,bottomMargin=16*mm)
    styles=getSampleStyleSheet(); story=[]
    esc=lambda s: str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    story += [Paragraph('PHANTOM TEAM — WHATSAPP TRACE X',styles['Title']),Paragraph('Blackmail Evidence Case Report',styles['Heading2']),Spacer(1,8)]
    c=data['case']
    for label,val in [('Case ID',c['id']),('Title',c['title']),('Created',c['created_at']),('Phone (user supplied)',c['phone_number'] or 'Not supplied'),('Case notes',c['notes'] or 'None')]:
        story.append(Paragraph(f'<b>{label}:</b> {esc(val)}',styles['BodyText']))
    story.append(Spacer(1,10)); story.append(Paragraph('Evidence register',styles['Heading2']))
    rows=[['ID','Original file','Size','SHA-256']]
    for e in data['evidence']: rows.append([str(e['id']),esc(e['original_name']),str(e['size_bytes']),e['sha256']])
    t=Table(rows,repeatRows=1,colWidths=[12*mm,48*mm,18*mm,95*mm]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#263445')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.3,colors.grey),('FONTSIZE',(0,0),(-1,-1),6),('VALIGN',(0,0),(-1,-1),'TOP')])); story.append(t)
    story += [Spacer(1,10),Paragraph('Notes / timeline',styles['Heading2'])]
    for n in data['notes']: story.append(Paragraph(esc(n['created_at'])+' — '+esc(n['body']),styles['BodyText']))
    story += [Spacer(1,12),Paragraph('<b>Important:</b> Keyword matches and number-format checks are preliminary only. This report does not identify a person, prove wrongdoing, or establish ownership of a phone number. Preserve original evidence and provide it to the appropriate authorities.',styles['Italic'])]
    doc.build(story); return out

# initialize schema on import
with connect(): pass
