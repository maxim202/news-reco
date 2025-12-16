"""Train and save ML models."""
import logging
import pickle
from pathlib import Path

import pandas as pd

from src.ml.recommender import ContentBasedRecommender

logger = logging.getLogger(__name__)


class RecommenderTrainer:
    """Train and manage recommender models."""

    def __init__(self, model_dir: str = "data/models"):
        """Initialize trainer."""
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.recommender = None

    def train_from_csv(self, csv_file: Path) -> ContentBasedRecommender:
        """
        Train recommender from processed CSV file.

        Args:
            csv_file: Path to processed CSV file

        Returns:
            Trained recommender
        """
        logger.info(f"Loading data from {csv_file.name}...")
        df = pd.read_csv(csv_file)

        logger.info(f"Training recommender on {len(df)} articles...")

        # Create article mapping with unique IDs
        df["article_id"] = range(len(df))

        # Train recommender
        self.recommender = ContentBasedRecommender()
        self.recommender.fit(df)

        # Log statistics
        stats = self.recommender.get_statistics()
        logger.info(f" Training completed!")
        logger.info(f"   Vocabulary size: {stats['vocabulary_size']}")
        logger.info(f"   Sparsity: {stats['sparsity']:.2%}")

        return self.recommender

    def save_model(self, filename: str = "recommender.pkl") -> Path:
        """
        Save trained model to disk.

        Args:
            filename: Output filename

        Returns:
            Path to saved model
        """
        if self.recommender is None:
            raise ValueError("No trained model to save")

        filepath = self.model_dir / filename

        with open(filepath, "wb") as f:
            pickle.dump(self.recommender, f)

        logger.info(f"✅ Model saved to {filepath}")
        return filepath

    def load_model(self, filename: str = "recommender.pkl") -> ContentBasedRecommender:
        """
        Load model from disk.

        Args:
            filename: Model filename

        Returns:
            Loaded recommender
        """
        filepath = self.model_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Model not found: {filepath}")

        with open(filepath, "rb") as f:
            self.recommender = pickle.load(f)

        logger.info(f"Model loaded from {filepath}")
        return self.recommender
