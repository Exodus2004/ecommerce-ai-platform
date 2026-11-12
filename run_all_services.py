"""
Master Local Launcher for the 5 Microservices:
Spins up all 5 microservices in parallel on distinct ports:
  1. API Gateway & Frontend     -> http://localhost:8000
  2. Catalog Service            -> http://localhost:8001
  3. AI Search Service          -> http://localhost:8002
  4. AI Recommendation Service  -> http://localhost:8003
  5. AI Chatbot Service         -> http://localhost:8004
"""

import sys
import os
import subprocess
import time
import signal

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SERVICES = [
    {
        "name": "📦 Catalog Service",
        "port": 8001,
        "dir": os.path.join(BASE_DIR, "services", "catalog"),
        "cmd": [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8001"]
    },
    {
        "name": "🔍 AI Search Service",
        "port": 8002,
        "dir": os.path.join(BASE_DIR, "services", "search"),
        "cmd": [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8002"]
    },
    {
        "name": "✨ AI Recommender Service",
        "port": 8003,
        "dir": os.path.join(BASE_DIR, "services", "recommendation"),
        "cmd": [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8003"]
    },
    {
        "name": "💬 AI Chatbot Service",
        "port": 8004,
        "dir": os.path.join(BASE_DIR, "services", "chatbot"),
        "cmd": [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8004"]
    },
    {
        "name": "🌐 API Gateway & Frontend",
        "port": 8000,
        "dir": os.path.join(BASE_DIR, "services", "gateway"),
        "cmd": [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]
    }
]

processes = []


def cleanup(signum=None, frame=None):
    print("\n🛑 Shutting down all 5 microservices...")
    for p, s in processes:
        try:
            p.terminate()
            p.kill()
        except Exception:
            pass
    print("✅ All services stopped.")
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup)
if sys.platform == "win32":
    signal.signal(signal.SIGTERM, cleanup)


def main():
    print("=" * 70)
    print("🚀 LAUNCHING 5 E-COMMERCE AI MICROSERVICES...")
    print("=" * 70)

    for s in SERVICES:
        print(f"Starting {s['name']} on port {s['port']}...")
        p = subprocess.Popen(
            s["cmd"],
            cwd=s["dir"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        processes.append((p, s))
        time.sleep(1.0)

    print("=" * 70)
    print("✅ ALL 5 MICROSERVICES ARE ONLINE!")
    print("🌐 Open the E-Commerce Store at:  http://localhost:8000")
    print("🏥 Check Cluster Health at:       http://localhost:8000/api/health")
    print("=" * 70)
    print("Press Ctrl+C to stop all services.")
    print("=" * 70)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
