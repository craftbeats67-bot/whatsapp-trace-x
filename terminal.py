from pathlib import Path
from core import list_cases,create_case,get_case,add_evidence,add_note,verify_evidence,build_report,inspect_invitation,validate_phone

def ask_case():
    cases=list_cases()
    if not cases: print('No cases yet.'); return None
    for c in cases: print(f"#{c['id']} | {c['title']} | {c['created_at']}")
    try: cid=int(input('Enter Case ID: ').strip())
    except ValueError: print('Enter numeric Case ID.'); return None
    return cid if get_case(cid) else None

def main():
    while True:
        print('\n=== WHATSAPP TRACE X | PHANTOM TEAM ===')
        print('1 Create case  2 List cases  3 View case  4 Add evidence  5 Add timeline note')
        print('6 Verify evidence hash  7 Generate PDF report  8 Inspect phone format  9 Inspect invitation text/link  0 Exit')
        choice=input('Select: ').strip()
        try:
            if choice=='1':
                title=input('Case title: '); notes=input('Initial notes: ')
                cc=input('Country code (e.g. +91, blank to skip): ').strip(); phone=input('Phone number without country code (blank to skip): ').strip()
                cid=create_case(title,notes,cc,phone); print(f'Created case #{cid}')
            elif choice=='2':
                for c in list_cases(): print(f"#{c['id']} | {c['title']} | {c['phone_number']} | {c['created_at']}")
            elif choice=='3':
                cid=ask_case()
                if cid:
                    d=get_case(cid); print(d['case'])
                    for e in d['evidence']: print(f"Evidence #{e['id']} {e['original_name']} SHA256={e['sha256']}")
                    for n in d['notes']: print(f"NOTE {n['created_at']}: {n['body']}")
            elif choice=='4':
                cid=ask_case()
                if cid:
                    p=input('Path to evidence file: ').strip().strip('"'); eid=add_evidence(cid,p); print(f'Added evidence #{eid}')
            elif choice=='5':
                cid=ask_case()
                if cid: add_note(cid,input('Timeline note: ')); print('Note saved.')
            elif choice=='6':
                try: eid=int(input('Evidence ID: ')); print(verify_evidence(eid))
                except ValueError as e: print(e)
            elif choice=='7':
                cid=ask_case()
                if cid: print('PDF saved:',build_report(cid))
            elif choice=='8':
                cc=input('Country code (e.g. +91): '); num=input('Phone number (without country code): ')
                print(validate_phone(cc,num))
            elif choice=='9':
                print('Paste invitation message/link text. End input with a single line containing .END')
                lines=[]
                while True:
                    line=input()
                    if line=='.END': break
                    lines.append(line)
                print(inspect_invitation('\\n'.join(lines)))
            elif choice=='0': print('Bye.'); break
            else: print('Invalid option.')
        except Exception as e: print('ERROR:',e)
if __name__=='__main__': main()
