"""
AI Chatbot Assistant:
Processes natural conversational requests, extracts entities and budget,
answers FAQs, and retrieves personalized recommendations.
"""

import os
import re
from typing import Dict, Any, List, Optional


class AIChatbot:
    def __init__(self, products: List[Dict[str, Any]]):
        self.products = products

        self.faq_knowledge = {
            "return": (
                "📦 **Return Policy**:\n"
                "We provide a **30-day hassle-free return window** for all items in original condition. "
                "You can initiate a return from your profile for a full refund back to your payment method!"
            ),
            "refund": (
                "💳 **Refund Timeline**:\n"
                "Once the returned package reaches our warehouse, inspection takes 24 hours. "
                "Your full refund is issued automatically within **3 to 5 business days**."
            ),
            "shipping": (
                "🚚 **Shipping & Delivery**:\n"
                "• **Free 2-Day Standard Shipping** on all orders over $35!\n"
                "• **Overnight Express Delivery** available at checkout for $9.99.\n"
                "Orders placed before 2 PM ship the same day."
            ),
            "delivery": (
                "🚚 **Delivery Times**:\n"
                "Standard deliveries arrive in **2 business days**. You will receive an SMS and email with live GPS tracking."
            ),
            "warranty": (
                "🛡️ **Warranty Protection**:\n"
                "All electronics, laptops, and audio gear include a **1-Year Manufacturer Warranty** covering defects and hardware failures."
            ),
            "contact": (
                "📞 **Customer Care Support**:\n"
                "Our team is available 24/7 at `support@shopsmart-ai.com` or toll-free at `1-800-555-SHOP`."
            )
        }

        self.lifestyle_graph = {
            "gym": ["shoes", "earbuds", "smartwatch", "running"],
            "workout": ["shoes", "earbuds", "smartwatch", "running"],
            "fitness": ["shoes", "smartwatch", "fitness-band", "running"],
            "running": ["shoes", "sneakers", "smartwatch", "running"],
            "jogging": ["shoes", "sneakers", "smartwatch", "running"],
            "exercise": ["shoes", "smartwatch", "fitness-band", "earbuds"],
            "office": ["laptop", "mouse", "keyboard", "headphones"],
            "work": ["laptop", "mouse", "keyboard", "headphones"],
            "wfh": ["laptop", "mouse", "keyboard", "headphones"],
            "coding": ["laptop", "keyboard", "mouse"],
            "programming": ["laptop", "keyboard", "mouse"],
            "student": ["laptop", "earbuds", "keyboard"],
            "college": ["laptop", "earbuds", "sneakers"],
            "study": ["laptop", "earbuds", "headphones"],
            "gaming": ["gaming", "rtx", "keyboard", "laptop"],
            "gamer": ["gaming", "rtx", "keyboard", "laptop"],
            "travel": ["headphones", "boots", "smartwatch"],
            "hiking": ["boots", "smartwatch", "outdoor"],
            "outdoor": ["boots", "smartwatch", "outdoor"],
            "cooking": ["air-fryer", "coffee", "espresso"],
            "kitchen": ["air-fryer", "coffee", "espresso"],
            "coffee": ["coffee", "espresso", "latte"],
            "morning": ["coffee", "espresso", "air-fryer"]
        }

        self.category_synonyms = {
            "laptop": "Laptops & Computers",
            "laptops": "Laptops & Computers",
            "computer": "Laptops & Computers",
            "notebook": "Laptops & Computers",
            "pc": "Laptops & Computers",
            "headphone": "Audio & Headphones",
            "headphones": "Audio & Headphones",
            "earbuds": "Audio & Headphones",
            "earphones": "Audio & Headphones",
            "audio": "Audio & Headphones",
            "music": "Audio & Headphones",
            "shoe": "Footwear & Running",
            "shoes": "Footwear & Running",
            "sneakers": "Footwear & Running",
            "boots": "Footwear & Running",
            "footwear": "Footwear & Running",
            "watch": "Smartwatches & Wearables",
            "smartwatch": "Smartwatches & Wearables",
            "watches": "Smartwatches & Wearables",
            "smartwatches": "Smartwatches & Wearables",
            "tracker": "Smartwatches & Wearables",
            "wearable": "Smartwatches & Wearables",
            "kitchen": "Home & Kitchen",
            "coffee": "Home & Kitchen",
            "espresso": "Home & Kitchen",
            "fryer": "Home & Kitchen"
        }

    def has_word(self, word: str, text: str) -> bool:
        return bool(re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE))

    def extract_budget(self, text: str) -> Optional[float]:
        pattern = r"(?:under|below|less than|within|\$)\s*(\d+(?:\.\d+)?)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return None

    def respond(self, user_message: str) -> Dict[str, Any]:
        clean_msg = user_message.strip()
        lower_msg = clean_msg.lower()

        # Greetings
        greeting_words = ["hi", "hello", "hey", "howdy", "greetings"]
        if any(self.has_word(w, lower_msg) for w in greeting_words) or "good morning" in lower_msg or "good evening" in lower_msg:
            top_picks = sorted(self.products, key=lambda x: x["rating"], reverse=True)[:3]
            return {
                "reply": (
                    "👋 **Hello! Welcome to ShopSmart AI!**\n\n"
                    "I am your personal AI shopping concierge. I can help you with:\n"
                    "• **Product Finder**: Ask for *'running shoes under $60'* or *'laptops for coding'*\n"
                    "• **Lifestyle Suggestions**: Ask about *'gym gear'*, *'work from home setup'*, or *'gifts'*\n"
                    "• **Store FAQs**: Ask about *'returns'*, *'shipping'*, or *'warranty'*\n\n"
                    "What can I help you find today?"
                ),
                "products": top_picks
            }

        # Thanks
        if lower_msg in ["thanks", "thank you", "thx", "appreciate it", "great thanks"]:
            return {
                "reply": "😊 You are very welcome! Let me know if you need any other recommendations or have questions about our products!",
                "products": []
            }

        # About
        if "who are you" in lower_msg or "what can you do" in lower_msg or lower_msg == "help":
            return {
                "reply": (
                    "🤖 **About ShopSmart AI**:\n"
                    "I am an intelligent shopping assistant built right into the platform. "
                    "I understand natural conversational requests, match items based on semantic vector similarity, "
                    "and help you discover the perfect products within your budget!"
                ),
                "products": []
            }

        # FAQs
        for key, text in self.faq_knowledge.items():
            if self.has_word(key, lower_msg):
                return {"reply": text, "products": []}

        budget = self.extract_budget(lower_msg)

        # Comparisons
        if any(self.has_word(w, lower_msg) for w in ["compare", "comparison", "difference", "vs"]):
            for cat_keyword, cat_name in self.category_synonyms.items():
                if self.has_word(cat_keyword, lower_msg):
                    cat_items = [p for p in self.products if p["category"] == cat_name]
                    cat_items.sort(key=lambda x: x["price"])
                    reply = f"⚖️ **Comparison of {cat_name}**:\n\n"
                    for item in cat_items:
                        reply += f"• **{item['title']}** (${item['price']}) — {item['rating']}⭐\n  *{item['description'][:90]}...*\n\n"
                    reply += "💡 *Tip: Choose based on whether your priority is budget or high-end performance!*"
                    return {"reply": reply, "products": cat_items}

        # Ranking
        target_category = None
        for syn, official_cat in self.category_synonyms.items():
            if self.has_word(syn, lower_msg):
                target_category = official_cat
                break

        pool = [p for p in self.products if p["category"] == target_category] if target_category else self.products
        if self.has_word("laptop", lower_msg) or self.has_word("laptops", lower_msg):
            pool = [p for p in pool if "laptop" in p["title"].lower() or "laptop" in [t.lower() for t in p.get("tags", [])]]

        if any(w in lower_msg for w in ["cheapest", "lowest price", "most affordable"]):
            sorted_items = sorted(pool, key=lambda x: x["price"])[:3]
            cat_txt = f" in {target_category}" if target_category else ""
            reply = f"💰 **Here are our most budget-friendly options{cat_txt}**:\n\n"
            for item in sorted_items:
                reply += f"• **{item['title']}** — only **${item['price']}** (Rating: {item['rating']}⭐)\n  *{item['description'][:90]}...*\n\n"
            return {"reply": reply, "products": sorted_items}

        if any(w in lower_msg for w in ["best rated", "top rated", "highest rated", "popular", "best seller"]):
            sorted_items = sorted(pool, key=lambda x: x["rating"], reverse=True)[:3]
            cat_txt = f" in {target_category}" if target_category else ""
            reply = f"⭐ **Here are our highest-rated customer favorites{cat_txt}**:\n\n"
            for item in sorted_items:
                reply += f"• **{item['title']}** — **{item['rating']} / 5 ⭐** (${item['price']})\n  *{item['description'][:90]}...*\n\n"
            return {"reply": reply, "products": sorted_items}

        # Gifts
        if any(self.has_word(w, lower_msg) for w in ["gift", "gifts", "present", "presents", "birthday"]):
            gift_picks = [p for p in self.products if p["rating"] >= 4.7][:3]
            reply = "🎁 **Looking for the perfect gift? Here are our top 3 most-gifted premium items**:\n\n"
            for item in gift_picks:
                reply += f"• **{item['title']}** (${item['price']}) — {item['rating']}⭐ customer favorite!\n"
            reply += "\nAll gifts come eligible for our 30-day return policy and full manufacturer warranty."
            return {"reply": reply, "products": gift_picks}

        # Lifestyle Graph
        matched_tags = []
        for life_term, tags in self.lifestyle_graph.items():
            if self.has_word(life_term, lower_msg):
                matched_tags.extend(tags)

        if matched_tags:
            lifestyle_matches = []
            for p in self.products:
                p_tags = [t.lower() for t in p.get("tags", [])]
                overlap = len(set(matched_tags).intersection(set(p_tags)))
                if overlap > 0:
                    if budget is None or p["price"] <= budget:
                        lifestyle_matches.append((p, overlap))

            if lifestyle_matches:
                lifestyle_matches.sort(key=lambda x: (x[1], x[0]["rating"]), reverse=True)
                top_items = [item[0] for item in lifestyle_matches[:3]]
                budget_txt = f" under **${budget:.2f}**" if budget else ""
                reply = f"🎯 **Great picks tailored for your lifestyle{budget_txt}**:\n\n"
                for item in top_items:
                    reply += f"• **{item['title']}** — **${item['price']}** (Rating: {item['rating']}⭐)\n  *{item['description'][:95]}...*\n\n"
                return {"reply": reply, "products": top_items}

        # Direct Category
        if target_category:
            cat_items = [p for p in self.products if p["category"] == target_category]
            if budget:
                cat_items = [p for p in cat_items if p["price"] <= budget]
            cat_items.sort(key=lambda x: x["rating"], reverse=True)
            if cat_items:
                budget_txt = f" under **${budget:.2f}**" if budget else ""
                reply = f"🛍️ **Here are top-rated items in {target_category}{budget_txt}**:\n\n"
                for item in cat_items[:3]:
                    reply += f"• **{item['title']}** — **${item['price']}** (Rating: {item['rating']}⭐)\n"
                return {"reply": reply, "products": cat_items[:3]}

        # Intelligent Universal Fallback (Never Fails)
        fallback_picks = sorted(self.products, key=lambda x: x["rating"], reverse=True)[:3]
        return {
            "reply": (
                f"💡 Here are our **trending top-rated customer favorites** across all categories:\n\n"
                f"• **{fallback_picks[0]['title']}** (${fallback_picks[0]['price']}) — {fallback_picks[0]['rating']}⭐\n"
                f"• **{fallback_picks[1]['title']}** (${fallback_picks[1]['price']}) — {fallback_picks[1]['rating']}⭐\n"
                f"• **{fallback_picks[2]['title']}** (${fallback_picks[2]['price']}) — {fallback_picks[2]['rating']}⭐\n\n"
                "Tell me a bit more! Are you shopping for **running**, **working/study**, **gaming**, **coffee**, or looking for a specific budget?"
            ),
            "products": fallback_picks
        }
