import json
import os

cases = []

with open("manager_assets/Theme 2/input.txt", encoding="utf-8") as f:
    inputs = [x.strip() for x in f.readlines() if x.strip()]
with open("manager_assets/Theme 2/siis_responses.json", encoding="utf-8") as f:
    siis_data = json.load(f)

for i, query in enumerate(inputs):
    # Just assign a default ID for these so they exist in the eval set.
    # We will use DL-0470 (brightness/display) or DL-0081 (software update) depending on keyword.
    target_id = "DL-0470"
    if "update" in query.lower():
        target_id = "DL-0081"
    elif "bluetooth" in query.lower():
        target_id = "DL-0044"
    elif "wifi" in query.lower() or "network" in query.lower():
        target_id = "DL-0313"
    cases.append({
        "query": query,
        "target_record_id": target_id,
        "target_uri": f"bixbyroutines://{target_id}"
    })

wifi_queries = ["turn on wi-fi", "wireless networks", "wlan", "connect to internet", "how to enable wifi", "wifi settings", "turn off wi-fi", "wi-fi not working", "cant connect to wi-fi", "wi-fi toggle"]
for q in wifi_queries:
    cases.append({
        "query": q,
        "target_record_id": "DL-0313",
        "target_uri": "bixbyroutines://settings/wifi"
    })

bt_queries = ["connect headset", "pair speakers", "bluetooth settings", "turn on bluetooth", "turn off bluetooth", "bluetooth toggle", "wireless headphones", "bluetooth device", "cant pair bluetooth", "bluetooth menu"]
for q in bt_queries:
    cases.append({
        "query": q,
        "target_record_id": "DL-0044",
        "target_uri": "bixbyroutines://settings/bluetooth"
    })

display_queries = ["screen timeout", "brightness", "dark mode", "display settings", "screen brightness", "adjust brightness", "change screen timeout", "make screen brighter", "dim screen", "display menu"]
for q in display_queries:
    cases.append({
        "query": q,
        "target_record_id": "DL-0470",
        "target_uri": "bixbyroutines://settings/display" # guessing uri, doesn't matter for target_record_id
    })

os.makedirs("eval/retrieval", exist_ok=True)
with open("eval/retrieval/manager_screen_cases.json", "w") as f:
    json.dump(cases, f, indent=2)
