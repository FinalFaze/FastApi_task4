import app.db.models
from fastapi import FastAPI

from app.routers.users import router as users_router
from app.routers.categories import router as categories_router
from app.routers.locations import router as locations_router
from app.routers.posts import router as posts_router
from app.routers.comments import router as comments_router

app = FastAPI(title="Blogicum API", version="0.3.0")

app.include_router(users_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(locations_router, prefix="/api/v1")
app.include_router(posts_router, prefix="/api/v1")
app.include_router(comments_router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["health"])
def health():
    return {"status": "ok"}
