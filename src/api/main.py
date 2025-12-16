"""FastAPI application for News Recommendation Platform."""
import logging
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import pandas as pd

from src.ml.trainer import RecommenderTrainer
from src.warehouse.connection import DatabaseManager
from src.warehouse.queries import WarehouseQueries

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="News Recommendation Platform API",
    description="ML-powered news article recommendations",
    version="1.0.0",
)

# Global variables for loaded models/connections
recommender = None
db_manager = None
warehouse_queries = None


# Pydantic Models
class Article(BaseModel):
    """Article data model."""
    article_id: int
    title: str
    description: Optional[str] = None
    source: str
    url: str


class RecommendationResult(BaseModel):
    """Recommendation result model."""
    article_id: int
    title: str
    similarity_score: float = Field(..., ge=0, le=1)
    source: str


class RecommendationsResponse(BaseModel):
    """Response for recommendations endpoint."""
    query_article_id: int
    recommendations: List[RecommendationResult]
    count: int


class WarehouseStats(BaseModel):
    """Warehouse statistics model."""
    total_articles: int
    total_sources: int
    total_authors: int
    avg_word_count: int
    avg_content_length: int
    articles_with_image: int


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Load models on startup."""
    global recommender, db_manager, warehouse_queries
    
    logger.info("Starting up application...")
    
    try:
        # Load recommender model
        trainer = RecommenderTrainer()
        recommender = trainer.load_model("recommender.pkl")
        logger.info("✅ Recommender model loaded")
        
        # Connect to database
        db_manager = DatabaseManager()
        db_manager.connect()
        warehouse_queries = WarehouseQueries(db_manager)
        logger.info("✅ Database connected")
        
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global db_manager
    
    if db_manager:
        db_manager.disconnect()
        logger.info("✅ Database disconnected")


# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "News Recommendation Platform",
        "version": "1.0.0",
    }


# Recommendations endpoints
@app.get(
    "/recommendations/{article_id}",
    response_model=RecommendationsResponse,
    tags=["Recommendations"],
)
async def get_recommendations(
    article_id: int,
    n: int = Query(5, ge=1, le=20, description="Number of recommendations"),
):
    """
    Get article recommendations for a given article.

    Args:
        article_id: ID of the article
        n: Number of recommendations (1-20)

    Returns:
        List of recommended articles with similarity scores
    """
    if recommender is None:
        raise HTTPException(
            status_code=503,
            detail="Recommender model not loaded"
        )

    try:
        recommendations = recommender.recommend(
            article_id=article_id,
            n_recommendations=n
        )

        if not recommendations:
            raise HTTPException(
                status_code=404,
                detail=f"Article {article_id} not found"
            )

        return RecommendationsResponse(
            query_article_id=article_id,
            recommendations=[
                RecommendationResult(**rec)
                for rec in recommendations
            ],
            count=len(recommendations),
        )

    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/recommendations/search",
    response_model=RecommendationsResponse,
    tags=["Recommendations"],
)
async def search_recommendations(
    query: str = Query(..., min_length=10, description="Search query"),
    n: int = Query(5, ge=1, le=20, description="Number of recommendations"),
):
    """
    Get recommendations for a custom query.

    Args:
        query: Custom text query
        n: Number of recommendations (1-20)

    Returns:
        List of recommended articles
    """
    if recommender is None:
        raise HTTPException(
            status_code=503,
            detail="Recommender model not loaded"
        )

    try:
        recommendations = recommender.recommend_for_content(
            content=query,
            n_recommendations=n
        )

        if not recommendations:
            raise HTTPException(
                status_code=404,
                detail="No similar articles found"
            )

        return RecommendationsResponse(
            query_article_id=-1,
            recommendations=[
                RecommendationResult(**rec)
                for rec in recommendations
            ],
            count=len(recommendations),
        )

    except Exception as e:
        logger.error(f"Error searching recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Warehouse analytics endpoints
@app.get(
    "/analytics/warehouse-stats",
    response_model=WarehouseStats,
    tags=["Analytics"],
)
async def get_warehouse_stats():
    """Get overall warehouse statistics."""
    if warehouse_queries is None:
        raise HTTPException(
            status_code=503,
            detail="Database not connected"
        )

    try:
        stats = warehouse_queries.get_warehouse_summary()
        return WarehouseStats(**stats)

    except Exception as e:
        logger.error(f"Error getting warehouse stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/analytics/articles-by-source",
    tags=["Analytics"],
)
async def get_articles_by_source():
    """Get article count by source."""
    if warehouse_queries is None:
        raise HTTPException(
            status_code=503,
            detail="Database not connected"
        )

    try:
        data = warehouse_queries.get_articles_by_source()
        return {
            "count": len(data),
            "data": data,
        }

    except Exception as e:
        logger.error(f"Error getting articles by source: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/analytics/articles-by-author",
    tags=["Analytics"],
)
async def get_articles_by_author(
    limit: int = Query(10, ge=1, le=50),
):
    """Get top authors by article count."""
    if warehouse_queries is None:
        raise HTTPException(
            status_code=503,
            detail="Database not connected"
        )

    try:
        data = warehouse_queries.get_articles_by_author(limit=limit)
        return {
            "count": len(data),
            "data": data,
        }

    except Exception as e:
        logger.error(f"Error getting articles by author: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/analytics/content-distribution",
    tags=["Analytics"],
)
async def get_content_distribution():
    """Get content length distribution."""
    if warehouse_queries is None:
        raise HTTPException(
            status_code=503,
            detail="Database not connected"
        )

    try:
        data = warehouse_queries.get_content_length_distribution()
        return {
            "count": len(data),
            "data": data,
        }

    except Exception as e:
        logger.error(f"Error getting content distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "News Recommendation Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }
