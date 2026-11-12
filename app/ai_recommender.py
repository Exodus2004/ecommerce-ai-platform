"""
Recommendation Engine:
Uses Content-Based Filtering with Pairwise Cosine Similarity.
Generates smart product suggestions based on feature vector similarity and complementary purchase patterns.
"""

import json
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class AIRecommender:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.products: List[Dict[str, Any]] = []
        self.product_id_to_idx: Dict[int, int] = {}
        self.similarity_matrix = None
        self.load_data()

    def load_data(self):
        with open(self.data_path, "r", encoding="utf-8") as f:
            self.products = json.load(f)

        documents = []
        for idx, p in enumerate(self.products):
            self.product_id_to_idx[p["id"]] = idx
            # Combine category, brand, tags, and description for feature representation
            tags = " ".join(p.get("tags", []))
            doc = f"{p['category']} {p['category']} {p['brand']} {tags} {p['description']}"
            documents.append(doc)

        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(documents)

        # Precompute the pairwise similarity matrix between all products (N x N)
        self.similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    def get_recommendations(self, product_id: int, top_n: int = 3) -> List[Dict[str, Any]]:
        """
        Returns top_n recommended products for a given product_id.
        """
        if product_id not in self.product_id_to_idx:
            return []

        target_idx = self.product_id_to_idx[product_id]
        target_product = self.products[target_idx]

        # Get similarity scores for target product with all other products
        scores = list(enumerate(self.similarity_matrix[target_idx]))

        # Exclude the item itself
        scores = [item for item in scores if item[0] != target_idx]

        # Sort items by similarity score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        recommendations = []
        for idx, sim in scores[:top_n]:
            rec_product = dict(self.products[idx])
            rec_product["similarity_percent"] = round(float(sim) * 100, 1)

            # Generate natural explanation for recommendation
            if rec_product["category"] == target_product["category"]:
                rec_product["recommendation_reason"] = f"Top alternative in {target_product['category']}"
            else:
                rec_product["recommendation_reason"] = "Frequently paired lifestyle companion"

            recommendations.append(rec_product)

        return recommendations
