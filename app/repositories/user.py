from sqlalchemy.orm import Session

from app.db.models import User
from app.domain.entities import UserEntity
from app.repositories.base import BaseRepository
from app.repositories.mappers import to_user_entity


class UserRepository(BaseRepository[User, UserEntity]):
    def __init__(self, db: Session):
        super().__init__(db, User, to_user_entity)
