import re

# Supports common WhatsApp text exports:
# 12/03/2025, 9:41 pm - Name: message
# [12/03/25, 21:41:00] Name: message
PATTERNS = {
    "Threat / intimidation": [
        r"\b(blackmail|leak|viral|expose|badnaam|dhamki|threat)\b",
        r"(photo|video|picture).{0,35}(leak|viral|share|public)",
        r"(leak|viral|share|public).{0,35}(photo|video|picture)"
    ],
    "Money demand": [
        r"\b(pay|payment|money|paise|rupees|₹|upi|transfer)\b"
    ],
    "Coercion / pressure": [
        r"\b(or else|otherwise|warna|nahi to|do this|karna padega)\b"
    ]
}

LINE_PATTERNS = [
    re.compile(r"^\[([^\]]+)\]\s+([^:]+?):\s?(.*)$"),
    re.compile(r"^(\d{1,2}[/-]\d{1,2}[/-]\d{2,4},?\s+\d{1,2}:\d{2}(?:\s?[ap]m)?)\s+-\s+([^:]+?):\s?(.*)$", re.I)
]

def parse_chat(text):
    messages, current = [], None
    for line in text.splitlines():
        matched = None
        for pattern in LINE_PATTERNS:
            m = pattern.match(line)
            if m:
                matched = m.groups()
                break
        if matched:
            if current:
                messages.append(current)
            current = {"time": matched[0].strip(), "sender": matched[1].strip(), "message": matched[2].strip()}
        elif current and line.strip():
            current["message"] += "\n" + line.strip()
    if current:
        messages.append(current)
    return messages

def analyze_messages(messages):
    results = []
    for item in messages:
        body = item["message"]
        lowered = body.lower()
        categories = []
        for category, patterns in PATTERNS.items():
            if any(re.search(p, lowered, re.I | re.S) for p in patterns):
                categories.append(category)
        for category in categories:
            results.append({
                "time": item["time"],
                "message": body[:2000],
                "category": category
            })
    return results
