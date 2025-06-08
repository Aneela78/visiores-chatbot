from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
from sklearn.neighbors import NearestNeighbors
from typing import List, Optional
from pathlib import Path

# Configuration
class Config:
    MODELS_DIR = Path(__file__).parent / "models"
    MAX_RESULTS = 10

# Response Models
class SearchResult(BaseModel):
    id: int
    title: str
    authors: str
    abstract: str
    similarity: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    count: int

# Initialize FastAPI app
app = FastAPI(
    title="ArXiv Search API",
    description="REST API for searching arXiv papers",
    version="1.0.0"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models and data
def load_resources():
    try:
        vectorizer = joblib.load(Config.MODELS_DIR / "vectorizer.pkl")
        model = joblib.load(Config.MODELS_DIR / "model.pkl")
        df = pd.read_csv(Config.MODELS_DIR / "arxiv_articles.csv")
        return vectorizer, model, df
    except Exception as e:
        raise RuntimeError(f"Failed to load resources: {str(e)}")

try:
    print("Loading resources...") 
    vectorizer, model, df = load_resources()
    print("Resources loaded successfully!")
except Exception as e:
    print(f"Error during startup: {str(e)}")
    raise

# API Endpoints
@app.get("/api/search", response_model=SearchResponse)
async def search_papers(
    q: str = Query(..., min_length=2, max_length=100),
    limit: Optional[int] = Query(5, ge=1, le=Config.MAX_RESULTS)
):
    """
    Search arXiv papers by semantic similarity
    """
    try:
        # Transform query to vector
        query_vec = vectorizer.transform([q])
        
        # Find nearest neighbors
        distances, indices = model.kneighbors(query_vec, n_neighbors=limit)
        
        # Prepare results
        results = []
        for i, idx in enumerate(indices[0]):
            results.append(SearchResult(
                id=int(idx),
                title=df.loc[idx, 'title'],
                authors=df.loc[idx, 'authors'],
                abstract=df.loc[idx, 'abstract'],
                similarity=float(1 - distances[0][i])  # Convert to similarity score
            ))
        
        return SearchResponse(
            query=q,
            results=results,
            count=len(results)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

@app.get("/api/health")
async def health_check():
    """Service health check"""
    return {"status": "healthy", "model_loaded": vectorizer is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)