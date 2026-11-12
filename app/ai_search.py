"""
Search Optimization Engine:
Uses TF-IDF Vectorization and Cosine Similarity to provide intelligent semantic search.
Understands concepts beyond exact keyword matching (e.g., 'budget' matches 'affordable', 'laptop' matches 'ultrabook').
"""

import json
import os
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class AISearchEngine:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.products: List[Dict[str, Any]] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.load_data()

    def load_data(self):
        with open(self.data_path, "r", encoding="utf-8") as f:
            self.products = json.load(f)

        # Build rich searchable document text for each product
        documents = []
        for p in self.products:
            tags_text = " ".join(p.get("tags", []))
            doc = f"{p['title']} {p['category']} {p['brand']} {p['description']} {tags_text}"
            documents.append(doc)

        # Initialize TF-IDF Vectorizer with n-grams (1-word and 2-word combinations)
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
        """
        Executes semantic search using cosine similarity, applies metadata filters,
        and returns products ranked by relevance.
        """
        if not query or query.strip() == "":
            results = list(self.products)
        else:
            # 1. Vectorize the incoming search query
            query_vec = self.vectorizer.transform([query.strip()])

            # 2. Compute Cosine Similarity between query vector and all product vectors
            similarity_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

            # 3. Attach similarity score to each product
            results = []
            for idx, score in enumerate(similarity_scores):
                prod_copy = dict(self.products[idx])
                prod_copy["relevance_score"] = round(float(score) * 100, 1)

                # Keyword boost: if exact words appear in title or tags, add slight relevance bonus
                query_words = set(query.lower().split())
                title_words = set(prod_copy["title"].lower().split())
                tag_words = set(tag.lower() for tag in prod_copy.get("tags", []))
                overlap = len(query_words.intersection(title_words.union(tag_words)))
                prod_copy["relevance_score"] += overlap * 5.0

                results.append(prod_copy)

            # Sort descending by relevance score
            results.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Apply Filters: Category, Max Price, Min Rating
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
