"""
AI Recommendation Engine:
Pairwise Cosine Similarity Content-Based Filtering.
"""

from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class AIRecommender:
    def __init__(self, products: List[Dict[str, Any]]):
        self.products = products
        self.product_id_to_idx: Dict[int, int] = {}
        self.similarity_matrix = None
        self.build_matrix()

    def build_matrix(self):
        documents = []
        for idx, p in enumerate(self.products):
            self.product_id_to_idx[p["id"]] = idx
            tags = " ".join(p.get("tags", []))
            doc = f"{p['category']} {p['category']} {p['brand']} {tags} {p['description']}"
            documents.append(doc)

        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(documents)
        self.similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    def get_recommendations(self, product_id: int, top_n: int = 3) -> List[Dict[str, Any]]:
        if product_id not in self.product_id_to_idx:
            return []

        target_idx = self.product_id_to_idx[product_id]
        target_product = self.products[target_idx]
        scores = list(enumerate(self.similarity_matrix[target_idx]))
        scores = [item for item in scores if item[0] != target_idx]
        scores.sort(key=lambda x: x[1], reverse=True)

        recommendations = []
        for idx, sim in scores[:top_n]:
            rec_product = dict(self.products[idx])
            rec_product["similarity_percent"] = round(float(sim) * 100, 1)

            if rec_product["category"] == target_product["category"]:
                rec_product["recommendation_reason"] = f"Top alternative in {target_product['category']}"
            else:
                rec_product["recommendation_reason"] = "Frequently paired lifestyle companion"

            recommendations.append(rec_product)

        return recommendations
