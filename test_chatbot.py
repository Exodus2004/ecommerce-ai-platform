import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from app.ai_search import AISearchEngine
from app.ai_recommender import AIRecommender
from app.ai_chatbot import AIChatbot

se = AISearchEngine("data/products.json")
rec = AIRecommender("data/products.json")
bot = AIChatbot(se, rec)

queries = [
    "headphones under $50",
    "laptop for coding",
    "do you have a coffee machine?",
    "how fast is shipping?"
]

print("=" * 60)
for q in queries:
    ans = bot.respond(q)
    print(f"User: '{q}'")
    print(f"Bot Reply:\n{ans['reply']}")
    print(f"Products Attached: {len(ans['products'])}")
    print("-" * 60)
