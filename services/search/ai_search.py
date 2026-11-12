"""
AI Search Engine:
Vector-based semantic search using TF-IDF and Cosine Similarity.
"""

import json
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class AISearchEngine:
    def __init__(self, products: List[Dict[str, Any]]):
        self.products = products
        self.vectorizer = None
        self.tfidf_matrix = None
        self.build_index()

    def build_index(self):
        documents = []
        for p in self.products:
            tags_text = " ".join(p.get("tags", []))
            doc = f"{p['title']} {p['category']} {p['brand']} {p['description']} {tags_text}"
            documents.append(doc)

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            lowercase=True
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        if not query or query.strip() == "":
            results = list(self.products)
        else:
            query_vec = self.vectorizer.transform([query.strip()])
            similarity_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

            results = []
            for idx, score in enumerate(similarity_scores):
                prod_copy = dict(self.products[idx])
                prod_copy["relevance_score"] = round(float(score) * 100, 1)

                query_words = set(query.lower().split())
                title_words = set(prod_copy["title"].lower().split())
                tag_words = set(tag.lower() for tag in prod_copy.get("tags", []))
                overlap = len(query_words.intersection(title_words.union(tag_words)))
                prod_copy["relevance_score"] += overlap * 5.0

                results.append(prod_copy)

            results.sort(key=lambda x: x["relevance_score"], reverse=True)

        filtered = []
        for p in results:
            if category and category.lower() != "all" and p["category"].lower() != category.lower():
                continue
            if max_price is not None and p["price"] > max_price:
                continue
            if min_rating is not None and p["rating"] < min_rating:
                continue
            filtered.append(p)

        return filtered[:top_k]
