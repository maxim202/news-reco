"""Run the FastAPI application."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.logging_config import setup_logging

logger = setup_logging()


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting News Recommendation API...")
    logger.info("📍 API running at http://localhost:8000")
    logger.info("📚 Docs available at http://localhost:8000/docs")
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
