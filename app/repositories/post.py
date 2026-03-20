from sqlalchemy.orm import Session

from app.db.models import Post
from app.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    def __init__(self, db: Session):
        super().__init__(db, Post)
