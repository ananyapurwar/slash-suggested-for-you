from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from main import get_suggested_experiences
from typing import List, Dict, Any

app = FastAPI(title="Experience Recommendations API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Experience Recommendations API",
        "version": "1.0.0",
        "endpoints": {
            "suggested": "/suggested?user_id={user_id}&k={k}",
            "docs": "/docs"
        }
    }

@app.get("/suggested")
async def suggested_for_you(user_id: str, k: int = Query(5, ge=1, le=20)):
    """
    Get suggested experiences for a user based on their wishlist and viewed experiences.
    
    Args:
        user_id: The user's UUID
        k: Number of recommendations (1-20, default 5)
    
    Returns:
        List of recommended experiences
    """
    try:
        recs = get_suggested_experiences(user_id, k)
        return {
            "status": "success",
            "user_id": user_id,
            "count": len(recs),
            "recommendations": recs
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "user_id": user_id
        }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "experience-recommendations"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)