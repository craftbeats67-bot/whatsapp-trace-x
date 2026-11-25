import argparse, hashlib, json
from pathlib import Path
from analyzer import parse_chat, analyze_messages

def main():
    parser = argparse.ArgumentParser(description="WhatsApp Trace X - local chat evidence analyzer")
    parser.add_argument("chat_file", help="Path to a WhatsApp exported .txt chat")
    parser.add_argument("--json", dest="json_file", help="Optional output JSON path")
    args = parser.parse_args()
    path = Path(args.chat_file)
    if not path.is_file() or path.suffix.lower() != ".txt":
        raise SystemExit("Please provide an existing WhatsApp .txt export.")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    text = raw.decode("utf-8-sig", errors="replace")
    messages = parse_chat(text)
    findings = analyze_messages(messages)
    report = {
        "file": path.name,
        "sha256": digest,
        "messages_parsed": len(messages),
        "possible_indicators": findings,
        "notice": "Keyword flags are preliminary and require human review; they are not proof."
    }
    print(f"Messages parsed: {len(messages)}")
    print(f"SHA-256: {digest}")
    print(f"Possible indicators: {len(findings)}")
    for x in findings:
        print(f"[{x['category']}] {x['time']} :: {x['message']}")
    if args.json_file:
        Path(args.json_file).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved report: {args.json_file}")

if __name__ == "__main__":
    main()
