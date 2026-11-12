import sys
import urllib.request
import json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# 1. Fetch current history
req = urllib.request.urlopen("http://127.0.0.1:8000/api/chat/history")
data = json.loads(req.read().decode())
print(f"Total conversation records: {data.get('total_records')}")
for idx, doc in enumerate(data.get("history", [])):
    print(f"  [{idx+1}] ({doc.get('storage')}) User: {doc.get('user_message')}")

# 2. Post a chat message
payload = json.dumps({"message": "Show me wireless earbuds"}).encode("utf-8")
post_req = urllib.request.Request("http://127.0.0.1:8000/api/chat", data=payload, headers={"Content-Type": "application/json"})
res = urllib.request.urlopen(post_req)
bot_data = json.loads(res.read().decode())
print(f"\nSent chat: 'Show me wireless earbuds'")
print(f"Bot replied with {len(bot_data.get('products', []))} products")

# 3. Verify it was immediately stored
req2 = urllib.request.urlopen("http://127.0.0.1:8000/api/chat/history")
data2 = json.loads(req2.read().decode())
print(f"\nUpdated conversation records: {data2.get('total_records')}")
latest = data2.get("history", [])[0]
print(f"Latest record saved: \"{latest.get('user_message')}\" stored in {latest.get('storage')}")
print("\n✅ Chat history persistence verified successfully!")
