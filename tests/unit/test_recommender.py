"""Unit tests for recommendation system."""
import pytest
import pandas as pd
import numpy as np

from src.ml.recommender import ContentBasedRecommender
from src.ml.trainer import RecommenderTrainer


@pytest.fixture
def sample_articles():
    """Create sample articles for testing."""
    return pd.DataFrame({
        "article_id": [1, 2, 3, 4, 5],
        "title": [
            "Machine Learning Basics",
            "Deep Learning Tutorial",
            "Python Programming",
            "Neural Networks Guide",
            "Web Development Tips",
        ],
        "content": [
            "Machine learning is a subset of artificial intelligence. "
            "It focuses on algorithms that learn from data.",
            "Deep learning uses neural networks with multiple layers. "
            "It is powerful for computer vision and NLP.",
            "Python is a popular programming language. "
            "It is great for data science and web development.",
            "Neural networks are inspired by the brain. "
            "They consist of layers of interconnected neurons.",
            "Web development involves frontend and backend. "
            "HTML, CSS, and JavaScript are essential.",
        ],
        "source_name": ["Tech Blog", "AI News", "Python Weekly", "ML Times", "Web Dev"],
    })


class TestContentBasedRecommender:
    """Test ContentBasedRecommender class."""

    def test_init(self):
        """Test initialization."""
        recommender = ContentBasedRecommender()

        assert recommender.tfidf_matrix is None
        assert recommender.articles_df is None

    def test_fit(self, sample_articles):
        """Test fitting the recommender."""
        recommender = ContentBasedRecommender()
        recommender.fit(sample_articles)

        assert recommender.tfidf_matrix is not None
        assert len(recommender.articles_df) == 5
        assert recommender.tfidf_matrix.shape[0] == 5

    def test_fit_with_empty_dataframe(self):
        """Test fitting with empty dataframe."""
        recommender = ContentBasedRecommender()
        empty_df = pd.DataFrame({"content": []})

        with pytest.raises(ValueError):
            recommender.fit(empty_df)

    def test_fit_without_content_column(self):
        """Test fitting without content column."""
        recommender = ContentBasedRecommender()
        bad_df = pd.DataFrame({"title": ["Article 1"]})

        with pytest.raises(ValueError):
            recommender.fit(bad_df)

    def test_recommend(self, sample_articles):
        """Test getting recommendations."""
        recommender = ContentBasedRecommender()
        recommender.fit(sample_articles)

        # Get recommendations for first article (about ML)
        recommendations = recommender.recommend(
            article_id=1,
            n_recommendations=3
        )

        assert len(recommendations) <= 3
        assert all("title" in rec for rec in recommendations)
        assert all("similarity_score" in rec for rec in recommendations)

        # First recommendation should be the most similar
        if len(recommendations) > 0:
            assert recommendations[0]["similarity_score"] >= 0

    def test_recommend_for_content(self, sample_articles):
        """Test recommendations for arbitrary content."""
        recommender = ContentBasedRecommender()
        recommender.fit(sample_articles)

        # Query for ML-related content
        query = "I want to learn about machine learning and neural networks"
        recommendations = recommender.recommend_for_content(
            content=query,
            n_recommendations=3
        )

        assert len(recommendations) > 0
        assert all("title" in rec for rec in recommendations)

        # Should recommend ML/AI articles
        titles = [rec["title"].lower() for rec in recommendations]
        assert any("learning" in title or "neural" in title for title in titles)

    def test_get_statistics(self, sample_articles):
        """Test getting recommender statistics."""
        recommender = ContentBasedRecommender()
        recommender.fit(sample_articles)

        stats = recommender.get_statistics()

        assert "num_articles" in stats
        assert "feature_matrix_shape" in stats
        assert "vocabulary_size" in stats
        assert "sparsity" in stats

        assert stats["num_articles"] == 5
        assert stats["feature_matrix_shape"][0] == 5
        assert 0 <= stats["sparsity"] <= 1

    def test_recommend_nonexistent_article(self, sample_articles):
        """Test recommending for nonexistent article."""
        recommender = ContentBasedRecommender()
        recommender.fit(sample_articles)

        recommendations = recommender.recommend(
            article_id=9999,
            n_recommendations=3
        )

        assert len(recommendations) == 0


class TestRecommenderTrainer:
    """Test RecommenderTrainer class."""

    def test_init(self):
        """Test trainer initialization."""
        trainer = RecommenderTrainer()

        assert trainer.recommender is None
        assert trainer.model_dir.exists()

    def test_train_from_dataframe(self, sample_articles, tmp_path):
        """Test training from CSV."""
        # Save sample data to temp CSV
        csv_file = tmp_path / "test_articles.csv"
        sample_articles.to_csv(csv_file, index=False)

        trainer = RecommenderTrainer(model_dir=str(tmp_path))
        recommender = trainer.train_from_csv(csv_file)

        assert recommender is not None
        assert len(recommender.articles_df) == 5

    def test_save_and_load_model(self, sample_articles, tmp_path):
        """Test saving and loading model."""
        # Train
        csv_file = tmp_path / "test_articles.csv"
        sample_articles.to_csv(csv_file, index=False)

        trainer = RecommenderTrainer(model_dir=str(tmp_path))
        trainer.train_from_csv(csv_file)

        # Save
        model_path = trainer.save_model("test_model.pkl")
        assert model_path.exists()

        # Load
        trainer2 = RecommenderTrainer(model_dir=str(tmp_path))
        loaded_recommender = trainer2.load_model("test_model.pkl")

        assert loaded_recommender is not None
        assert len(loaded_recommender.articles_df) == 5

    def test_load_nonexistent_model(self, tmp_path):
        """Test loading nonexistent model."""
        trainer = RecommenderTrainer(model_dir=str(tmp_path))

        with pytest.raises(FileNotFoundError):
            trainer.load_model("nonexistent.pkl")

    def test_save_without_training(self, tmp_path):
        """Test saving without training first."""
        trainer = RecommenderTrainer(model_dir=str(tmp_path))

        with pytest.raises(ValueError):
            trainer.save_model()
