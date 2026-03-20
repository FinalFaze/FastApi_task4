from sqlalchemy.orm import Session

from app.db.models import Location
from app.repositories.base import BaseRepository


class LocationRepository(BaseRepository[Location]):
    def __init__(self, db: Session):
        super().__init__(db, Location)
