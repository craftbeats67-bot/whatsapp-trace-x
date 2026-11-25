from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort
from werkzeug.utils import secure_filename
from pathlib import Path
from datetime import datetime, timezone
import sqlite3, hashlib, json, re, os, io
from analyzer import parse_chat, analyze_messages

ROOT = Path(__file__).resolve().parent
DB = ROOT / "trace_x.db"
EVIDENCE = ROOT / "evidence"
REPORTS = ROOT / "reports"
ALLOWED = {".txt", ".png", ".jpg", ".jpeg", ".pdf"}
MAX_BYTES = 10 * 1024 * 1024

app = Flask(__name__)
app.secret_key = os.environ.get("TRACE_X_SECRET", "local-development-key-change-before-sharing")
app.config["MAX_CONTENT_LENGTH"] = MAX_BYTES

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            phone TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            original_name TEXT NOT NULL,
            stored_name TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            size INTEGER NOT NULL,
            kind TEXT NOT NULL,
            added_at TEXT NOT NULL,
            FOREIGN KEY(case_id) REFERENCES cases(id)
        );
        CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            source_evidence_id INTEGER NOT NULL,
            message_time TEXT DEFAULT '',
            message TEXT NOT NULL,
            category TEXT NOT NULL,
            FOREIGN KEY(case_id) REFERENCES cases(id),
            FOREIGN KEY(source_evidence_id) REFERENCES evidence(id)
        );
        """)
        con.commit()

def now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

@app.errorhandler(413)
def too_large(_):
    flash("File too large. Maximum upload size is 10 MB.", "error")
    return redirect(url_for("index"))

@app.route("/assets/<path:filename>")
def asset(filename):
    from flask import send_from_directory
    return send_from_directory(ROOT / "assets", filename)

@app.route("/", methods=["GET"])
def index():
    init_db()
    with db() as con:
        cases = con.execute("""
          SELECT c.*, COUNT(e.id) AS evidence_count
          FROM cases c LEFT JOIN evidence e ON e.case_id=c.id
          GROUP BY c.id ORDER BY c.id DESC
        """).fetchall()
        totals = {
            "cases": con.execute("SELECT COUNT(*) FROM cases").fetchone()[0],
            "evidence": con.execute("SELECT COUNT(*) FROM evidence").fetchone()[0],
            "findings": con.execute("SELECT COUNT(*) FROM findings").fetchone()[0]
        }
    return render_template("index.html", cases=cases, totals=totals)

@app.route("/case/new", methods=["POST"])
def new_case():
    title = request.form.get("title", "").strip()
    phone = request.form.get("phone", "").strip()
    notes = request.form.get("notes", "").strip()
    if not title:
        flash("Case title is required.", "error")
        return redirect(url_for("index"))
    if len(title) > 120 or len(phone) > 40 or len(notes) > 2000:
        flash("One or more fields are too long.", "error")
        return redirect(url_for("index"))
    with db() as con:
        cur = con.execute("INSERT INTO cases(title,phone,notes,created_at) VALUES(?,?,?,?)",
                          (title, phone, notes, now()))
        case_id = cur.lastrowid
        con.commit()
    flash(f"Case #{case_id} created.", "success")
    return redirect(url_for("case_detail", case_id=case_id))

@app.route("/case/<int:case_id>")
def case_detail(case_id):
    with db() as con:
        case = con.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
        if not case:
            abort(404)
        evidence = con.execute("SELECT * FROM evidence WHERE case_id=? ORDER BY id DESC", (case_id,)).fetchall()
        findings = con.execute("SELECT f.*,e.original_name FROM findings f JOIN evidence e ON e.id=f.source_evidence_id WHERE f.case_id=? ORDER BY f.id DESC", (case_id,)).fetchall()
    return render_template("case.html", case=case, evidence=evidence, findings=findings)

@app.route("/case/<int:case_id>/upload", methods=["POST"])
def upload(case_id):
    with db() as con:
        case = con.execute("SELECT id FROM cases WHERE id=?", (case_id,)).fetchone()
    if not case:
        abort(404)
    f = request.files.get("file")
    if not f or not f.filename:
        flash("Choose an evidence file first.", "error")
        return redirect(url_for("case_detail", case_id=case_id))
    original = secure_filename(f.filename)
    ext = Path(original).suffix.lower()
    if ext not in ALLOWED:
        flash("Allowed formats: TXT, PNG, JPG, JPEG, PDF.", "error")
        return redirect(url_for("case_detail", case_id=case_id))
    data = f.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        flash("File exceeds 10 MB.", "error")
        return redirect(url_for("case_detail", case_id=case_id))
    digest = hashlib.sha256(data).hexdigest()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    stored = f"case{case_id}_{stamp}{ext}"
    dest = EVIDENCE / stored
    dest.write_bytes(data)
    kind = "WhatsApp chat export" if ext == ".txt" else "Supporting attachment"
    with db() as con:
        cur = con.execute("""INSERT INTO evidence(case_id,original_name,stored_name,sha256,size,kind,added_at)
                             VALUES(?,?,?,?,?,?,?)""",
                          (case_id, original, stored, digest, len(data), kind, now()))
        evidence_id = cur.lastrowid
        con.commit()
    if ext == ".txt":
        try:
            text = data.decode("utf-8-sig", errors="replace")
            messages = parse_chat(text)
            findings = analyze_messages(messages)
            with db() as con:
                for item in findings:
                    con.execute("""INSERT INTO findings(case_id,source_evidence_id,message_time,message,category)
                                   VALUES(?,?,?,?,?)""",
                                (case_id, evidence_id, item["time"], item["message"], item["category"]))
                con.commit()
            flash(f"Chat imported. {len(messages)} messages parsed; {len(findings)} possible indicators flagged for human review.", "success")
        except Exception as exc:
            flash(f"File saved, but chat parsing failed: {exc}", "error")
    else:
        flash("Evidence saved locally and SHA-256 recorded. This file was not automatically analyzed.", "success")
    return redirect(url_for("case_detail", case_id=case_id))

@app.route("/evidence/<int:evidence_id>/download")
def download_evidence(evidence_id):
    with db() as con:
        item = con.execute("SELECT * FROM evidence WHERE id=?", (evidence_id,)).fetchone()
    if not item:
        abort(404)
    path = EVIDENCE / item["stored_name"]
    if not path.exists():
        abort(404)
    return send_file(path, as_attachment=True, download_name=item["original_name"])

@app.route("/case/<int:case_id>/report")
def report(case_id):
    with db() as con:
        case = con.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
        if not case:
            abort(404)
        evidence = con.execute("SELECT * FROM evidence WHERE case_id=? ORDER BY id", (case_id,)).fetchall()
        findings = con.execute("SELECT f.*,e.original_name FROM findings f JOIN evidence e ON e.id=f.source_evidence_id WHERE f.case_id=? ORDER BY f.id", (case_id,)).fetchall()
    payload = {
        "case": dict(case),
        "generated_at": now(),
        "notice": "Automated keyword flags are preliminary indicators, not proof that a person committed an offence. Verify context and preserve original evidence.",
        "evidence": [dict(x) for x in evidence],
        "possible_indicators": [dict(x) for x in findings]
    }
    out = REPORTS / f"case_{case_id}_report.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return send_file(out, as_attachment=True)

@app.route("/case/<int:case_id>/verify")
def verify(case_id):
    with db() as con:
        items = con.execute("SELECT * FROM evidence WHERE case_id=?", (case_id,)).fetchall()
    checks = []
    for item in items:
        path = EVIDENCE / item["stored_name"]
        actual = sha256_file(path) if path.exists() else "MISSING"
        checks.append({"name": item["original_name"], "stored": item["sha256"],
                       "current": actual, "match": actual == item["sha256"]})
    return render_template("verify.html", case_id=case_id, checks=checks)

if __name__ == "__main__":
    init_db()
    print("\\nPHANTOM TEAM | WHATSAPP TRACE X")
    print("BY KRRISH | @mahisec_13")
    print("Local-only dashboard: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
