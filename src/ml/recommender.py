"""Content-based recommendation system."""
import logging
from typing import List, Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class ContentBasedRecommender:
    """Content-based recommendation system using TF-IDF and cosine similarity."""

    def __init__(self, min_df: int = 1, max_df: float = 1.0):
        """
        Initialize recommender.

        Args:
            min_df: Minimum document frequency
            max_df: Maximum document frequency
        """
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            min_df=min_df,
            max_df=max_df,
            stop_words="english",
            ngram_range=(1, 2),
        )
        self.tfidf_matrix = None
        self.articles_df = None
        self.article_mapping = {}

    def fit(self, articles_df: pd.DataFrame) -> None:
        """
        Fit the recommender on articles.

        Args:
            articles_df: DataFrame with 'article_id', 'title', and 'content'
        """
        logger.info("Fitting content-based recommender...")

        if articles_df.empty:
            raise ValueError("Articles DataFrame is empty")

        if "content" not in articles_df.columns:
            raise ValueError("Articles must have 'content' column")

        # Store articles
        self.articles_df = articles_df.copy()

        # Create article mapping (article_id -> index)
        self.article_mapping = {
            idx: row["article_id"]
            for idx, row in articles_df.iterrows()
        }

        # Combine title and content for better features
        combined_text = (
            articles_df["title"].fillna("") + " " +
            articles_df["content"].fillna("")
        )

        # Fit and transform
        self.tfidf_matrix = self.vectorizer.fit_transform(combined_text)

        logger.info(
            f"Fitted recommender on {len(articles_df)} articles"
        )
        logger.info(
            f"   Feature matrix shape: {self.tfidf_matrix.shape}"
        )

    def recommend(
        self,
        article_id: int,
        n_recommendations: int = 5,
    ) -> List[Dict[str, any]]:
        """
        Recommend similar articles.

        Args:
            article_id: ID of article to find similar articles for
            n_recommendations: Number of recommendations to return

        Returns:
            List of recommended articles with similarity scores
        """
        if self.tfidf_matrix is None:
            raise ValueError("Recommender not fitted yet. Call fit() first.")

        # Find article index
        article_indices = [
            idx for idx, aid in self.article_mapping.items()
            if aid == article_id
        ]

        if not article_indices:
            logger.warning(f"Article {article_id} not found in corpus")
            return []

        article_idx = article_indices[0]

        # Calculate similarities
        similarities = cosine_similarity(
            self.tfidf_matrix[article_idx],
            self.tfidf_matrix
        )[0]

        # Get top similar articles (excluding the article itself)
        similar_indices = np.argsort(similarities)[::-1][1:n_recommendations + 1]

        recommendations = []
        for idx in similar_indices:
            article = self.articles_df.iloc[idx]
            recommendations.append({
                "article_id": article["article_id"],
                "title": article["title"],
                "similarity_score": float(similarities[idx]),
                "source": article.get("source_name", "Unknown"),
            })

        return recommendations

    def recommend_for_content(
        self,
        content: str,
        n_recommendations: int = 5,
    ) -> List[Dict[str, any]]:
        """
        Recommend articles similar to given content.

        Args:
            content: Text content to find similar articles for
            n_recommendations: Number of recommendations to return

        Returns:
            List of recommended articles with similarity scores
        """
        if self.tfidf_matrix is None:
            raise ValueError("Recommender not fitted yet. Call fit() first.")

        # Transform input content
        content_tfidf = self.vectorizer.transform([content])

        # Calculate similarities
        similarities = cosine_similarity(
            content_tfidf,
            self.tfidf_matrix
        )[0]

        # Get top similar articles
        similar_indices = np.argsort(similarities)[::-1][:n_recommendations]

        recommendations = []
        for idx in similar_indices:
            if similarities[idx] > 0:  # Only include positive similarities
                article = self.articles_df.iloc[idx]
                recommendations.append({
                    "article_id": article["article_id"],
                    "title": article["title"],
                    "similarity_score": float(similarities[idx]),
                    "source": article.get("source_name", "Unknown"),
                })

        return recommendations

    def get_statistics(self) -> Dict[str, any]:
        """Get recommender statistics."""
        if self.tfidf_matrix is None:
            return {}

        return {
            "num_articles": len(self.articles_df),
            "feature_matrix_shape": self.tfidf_matrix.shape,
            "vocabulary_size": len(self.vectorizer.get_feature_names_out()),
            "sparsity": 1 - (self.tfidf_matrix.nnz / 
                           (self.tfidf_matrix.shape[0] * 
                            self.tfidf_matrix.shape[1])),
        }
