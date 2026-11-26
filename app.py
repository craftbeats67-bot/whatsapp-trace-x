from flask import Flask, request, redirect, url_for, render_template, flash, send_file, abort
from pathlib import Path
import tempfile
from core import list_cases, create_case, get_case, add_evidence, add_note, verify_evidence, build_report, inspect_invitation, validate_phone
app=Flask(__name__); app.secret_key='local-only-change-this-key'

@app.get('/')
def index(): return render_template('index.html',cases=list_cases())
@app.post('/case')
def new_case():
    try:
        cid=create_case(request.form.get('title',''),request.form.get('notes',''),request.form.get('country_code',''),request.form.get('phone_number',''))
        flash(f'Case #{cid} created.'); return redirect(url_for('case_view',case_id=cid))
    except Exception as e: flash(str(e)); return redirect(url_for('index'))
@app.get('/case/<int:case_id>')
def case_view(case_id):
    data=get_case(case_id)
    if not data: abort(404)
    return render_template('case.html',data=data)
@app.post('/case/<int:case_id>/evidence')
def evidence(case_id):
    f=request.files.get('file')
    if not f or not f.filename: flash('Choose a file.'); return redirect(url_for('case_view',case_id=case_id))
    suffix=Path(f.filename).suffix.lower()
    with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
        f.save(tmp.name)
        try: eid=add_evidence(case_id,tmp.name,f.filename,f.mimetype); flash(f'Evidence #{eid} added and hashed.')
        except Exception as e: flash(str(e))
    return redirect(url_for('case_view',case_id=case_id))
@app.post('/case/<int:case_id>/note')
def note(case_id):
    try: add_note(case_id,request.form.get('body','')); flash('Note added.')
    except Exception as e: flash(str(e))
    return redirect(url_for('case_view',case_id=case_id))
@app.post('/inspect-number')
def inspect_number():
    ok,val=validate_phone(request.form.get('country_code',''),request.form.get('phone_number',''))
    return render_template('number.html',ok=ok,result=val)
@app.post('/inspect-link')
def inspect_link():
    result=inspect_invitation(request.form.get('text',''))
    return render_template('links.html',result=result)
@app.get('/case/<int:case_id>/report')
def report(case_id):
    try: return send_file(build_report(case_id),as_attachment=True,download_name=f'case_{case_id}_report.pdf')
    except ValueError: abort(404)
@app.get('/verify/<int:evidence_id>')
def verify(evidence_id):
    try: return render_template('verify.html',result=verify_evidence(evidence_id))
    except ValueError: abort(404)
if __name__=='__main__': app.run(host='127.0.0.1',port=5000,debug=False)
