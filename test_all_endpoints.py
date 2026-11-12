import sys
import urllib.request
import json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

tests = [
    ("Gateway Storefront", "http://127.0.0.1:8000/"),
    ("Gateway Cluster Health", "http://127.0.0.1:8000/api/health"),
    ("Gateway Products", "http://127.0.0.1:8000/products"),
    ("Gateway Search", "http://127.0.0.1:8000/search?q=shoes"),
    ("Gateway Recommend", "http://127.0.0.1:8000/recommend/1"),
    ("Gateway History (MongoDB)", "http://127.0.0.1:8000/history"),
    ("Gateway Swagger Docs", "http://127.0.0.1:8000/docs"),
    ("Catalog Root (Port 8001)", "http://127.0.0.1:8001/"),
    ("Catalog Products (PostgreSQL)", "http://127.0.0.1:8001/products"),
    ("Catalog Categories", "http://127.0.0.1:8001/categories"),
    ("Catalog Health", "http://127.0.0.1:8001/health"),
    ("Search Root (Port 8002)", "http://127.0.0.1:8002/"),
    ("Search AI Query (TF-IDF)", "http://127.0.0.1:8002/search?q=laptop"),
    ("Search Health", "http://127.0.0.1:8002/health"),
    ("Recommend Root (Port 8003)", "http://127.0.0.1:8003/"),
    ("Recommend AI Sim (Cosine)", "http://127.0.0.1:8003/recommend/1"),
    ("Recommend Health", "http://127.0.0.1:8003/health"),
    ("Chatbot Root (Port 8004)", "http://127.0.0.1:8004/"),
    ("Chatbot History (MongoDB)", "http://127.0.0.1:8004/chat/history"),
    ("Chatbot Health", "http://127.0.0.1:8004/health")
]

passed = 0
failed = 0

print("=" * 75)
print("VERIFYING ALL 5 MICROSERVICES & REVERSE PROXY ENDPOINTS")
print("=" * 75)

for label, url in tests:
    try:
        r = urllib.request.urlopen(url, timeout=3)
        print(f"[PASS] {label:32} [{url}] -> HTTP {r.status}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] {label:32} [{url}] -> ERROR: {e}")
        failed += 1

print("=" * 75)
print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests.")
print("=" * 75)
