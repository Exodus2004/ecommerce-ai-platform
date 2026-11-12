"""
Local Dev Server Launcher:
Runs the ShopSmart AI E-Commerce application on http://localhost:8000
"""
import uvicorn

if __name__ == "__main__":
    print("=" * 65)
    print("🚀 Starting ShopSmart AI E-Commerce Server...")
    print("🌐 Open in your browser: http://localhost:8000")
    print("=" * 65)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
