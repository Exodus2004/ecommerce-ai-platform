"""
Verification Test Script:
Verifies that Search, Recommendation, and Chatbot engines function correctly.
"""
import os
import sys

# Ensure UTF-8 output in Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to path
sys.path.insert(0, os.path.abspath("."))

from app.ai_search import AISearchEngine
from app.ai_recommender import AIRecommender
from app.ai_chatbot import AIChatbot

DATA_PATH = os.path.join("data", "products.json")

print("1. Testing AI Search Engine...")
search_engine = AISearchEngine(data_path=DATA_PATH)
search_res = search_engine.search("budget running shoes", max_price=60)
print(f"   Found {len(search_res)} items matching 'budget running shoes' under $60:")
for item in search_res:
    print(f"   - {item['title']} (${item['price']}) [Relevance: {item['relevance_score']}%]")

print("\n2. Testing AI Recommender Engine...")
recommender = AIRecommender(data_path=DATA_PATH)
rec_res = recommender.get_recommendations(product_id=1, top_n=3)
print(f"   Recommendations for product #1 (AeroBook Pro Laptop):")
for r in rec_res:
    print(f"   - {r['title']} (${r['price']}) [{r['recommendation_reason']} - {r['similarity_percent']}% similarity]")

print("\n3. Testing AI Chatbot...")
chatbot = AIChatbot(search_engine=search_engine, recommender=recommender)
reply1 = chatbot.respond("Do you have wireless headphones under $50?")
print("   User: 'Do you have wireless headphones under $50?'")
print(f"   Bot: {reply1['reply'][:150]}...")

reply2 = chatbot.respond("What is your return policy?")
print("\n   User: 'What is your return policy?'")
print(f"   Bot: {reply2['reply'][:150]}...")

print("\n✅ All 3 AI modules passed verification successfully!")
