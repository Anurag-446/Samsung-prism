"""
Regenerate eval/retrieval/manager_screen_cases.json with actual catalog URIs.
Uses manager input.txt queries with correct deeplink record IDs and URIs.
"""
import json
import os

# Load catalog
with open("manager_assets/Theme 2/deeplinks.json") as f:
    dls = json.load(f)
records = dls if isinstance(dls, list) else dls.get("deeplinks", [])
dl_by_id = {r["id"]: r for r in records}

# Map each input.txt query to the best-fit deeplink from catalog
# Based on the actual query intent:
INPUT_LABELS = [
    # query, record_id, rationale
    ("My TechCorp A15G tablet screen flashes and then goes completely blank whenever I tap to open an email in Gmail, and after it works for a short time it goes blank again.", "DL-0470", "Screen display issue -> Brightness settings"),
    ("My Nexa X1 screen turns completely blank or white and no text appears when I search for a stock price or use the Quick Assist app, and it happens with other apps too.", "DL-0470", "Screen blank -> display settings"),
    ("My Nexa Fold X1 screen went completely black, so I can't see or interact with the phone, and I'm unable to use Data Transfer or any other method to transfer my data.", "DL-0470", "Screen black -> display"),
    ("My TechCorp Nexa A14/A15 screen suddenly went completely black on its own after about a month of use. It doesn't display anything, even when I try to turn it on.", "DL-0470", "Screen blank -> display"),
    ("My tablet screen stays completely blank when I try to use Data Transfer to scan the QR code for transferring data from my Nexa X1 phone, so the transfer can't proceed.", "DL-0470", "Screen blank -> display"),
    ("My tablet's screen stays dark and only three app icons are lit while the rest are dark and won't open, so nothing loads on the screen and I can't use the device.", "DL-0470", "Screen dark -> display"),
    ("My new smartphone's main screen stays small and doesn't fill the whole display; I can't make it expand to full size and I've never seen this before.", "DL-0111", "Full screen in split screen view"),
    ("My Nexa Fold X1 inner screen stopped working by itself; it shows no image and doesn't respond to touch, while the outer cover screen still works.", "DL-0125", "Touch sensitivity issue"),
    ("My TechCorp Nexa Fold X1 screen flickers and goes blank whenever I open it, so I can't see anything or access the settings, which stops me from using the phone.", "DL-0021", "Enable Adaptive Display / brightness"),
    ("My Nexa Fold X1 screen is half black\u2014one side of the display is completely dark while the other side works fine, so I can't access the device normally.", "DL-0021", "Display/brightness"),
    ("My Nexa X1 has a floating circle that constantly hovers on my screen and gives me quick shortcuts to recent apps, home, back, screen off, volume control, and more; I want to remove it.", "DL-0110", "Floating notifications / Assistive menu"),
    ("My Nexa X1 screen stays blank and doesn't show any activation message or anything else when I turn it on after the carrier deactivated the old phone.", "DL-0470", "Screen blank -> display settings"),
    ("My smartphone's screen is completely cracked, it's a total crack and I can't use the device.", "DL-0083", "Diagnostic data / physical damage -> send diagnostic"),
    ("My Nexa X1 Ultra only shows a blue (or black) screen with tiny text when I try to turn it on, and it won't start up. I tried holding the power button but it doesn't help.", "DL-0470", "Screen startup issue -> display"),
    ("My TechCorp X1 Ultra screen flashes extremely quickly (in milliseconds) whenever I plug in a charger, making the display unusable for a short period.", "DL-0020", "Disable Adaptive Display / brightness flashing"),
    ('1. "My Nexa X1 screen goes completely blank, just a dark screen with occasional scrolling and no visible content, so I can\'t see anything or use Data Transfer to transfer data."', "DL-0470", "Screen blank -> display"),
    ('1. "My Nexa Fold X1 screen is cracked again right where it folds." 2. "The touch doesn\'t work on certain parts of the screen." 3. "I can hardly see anything on the display."', "DL-0125", "Touch sensitivity"),
    ("My Nexa A14 screen looks distorted right after I received the phone, and I need a diagnostic test.", "DL-0083", "Diagnostic test -> Send diagnostic data"),
    ("My Nexa X1 screen inputs are delayed and the touch responsiveness is laggy, causing a noticeable delay when I try to interact with the phone.", "DL-0125", "Touch sensitivity"),
    ("My Nexa X1 Ultra screen is completely black and won't turn on, even though the phone powers on, rings, and otherwise works; there is no physical damage.", "DL-0089", "Enable Double tap to turn on screen"),
]

# Build dataset
cases = []
for query, dl_id, rationale in INPUT_LABELS:
    record = dl_by_id.get(dl_id)
    if not record:
        print(f"WARNING: {dl_id} not found in catalog!")
        continue
    cases.append({
        "query": query,
        "target_record_id": dl_id,
        "target_uri": record["deeplink"],
        "rationale": rationale,
    })

os.makedirs("eval/retrieval", exist_ok=True)
with open("eval/retrieval/manager_screen_cases.json", "w", encoding="utf-8") as f:
    json.dump(cases, f, indent=2, ensure_ascii=False)

print(f"Written {len(cases)} cases to eval/retrieval/manager_screen_cases.json")
for c in cases:
    print(f"  [{c['target_record_id']}] {c['query'][:70]}...")
