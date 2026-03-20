from typing import Generic, Type, TypeVar

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.errors import (
    InfrastructureConflictError,
    InfrastructureDatabaseError,
    InfrastructureIntegrityError,
    InfrastructureNotFoundError,
)

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def list(self) -> list[T]:
        try:
            return self.db.query(self.model).order_by(self.model.id).all()
        except SQLAlchemyError as exc:
            raise InfrastructureDatabaseError(
                message=f"Failed to list {self.model.__name__}",
                entity=self.model.__name__,
                operation="list",
                details={"db_error": str(exc)},
            ) from exc

    def get(self, obj_id: int) -> T:
        try:
            obj = self.db.get(self.model, obj_id)
        except SQLAlchemyError as exc:
            raise InfrastructureDatabaseError(
                message=f"Failed to get {self.model.__name__}",
                entity=self.model.__name__,
                operation="get",
                details={"id": obj_id, "db_error": str(exc)},
            ) from exc
        if not obj:
            raise InfrastructureNotFoundError(
                message=f"{self.model.__name__} not found",
                entity=self.model.__name__,
                operation="get",
                details={"id": obj_id},
            )
        return obj

    def create(self, data: dict) -> T:
        obj = self.model(**data)
        self.db.add(obj)
        try:
            self.db.commit()
            self.db.refresh(obj)
        except IntegrityError as exc:
            self.db.rollback()
            raise self._map_integrity_error(exc, "create", data) from exc
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise InfrastructureDatabaseError(
                message=f"Failed to create {self.model.__name__}",
                entity=self.model.__name__,
                operation="create",
                details={"payload": sorted(data.keys()), "db_error": str(exc)},
            ) from exc
        return obj

    def update(self, obj_id: int, data: dict) -> T:
        obj = self.get(obj_id)
        for key, value in data.items():
            setattr(obj, key, value)
        try:
            self.db.commit()
            self.db.refresh(obj)
        except IntegrityError as exc:
            self.db.rollback()
            raise self._map_integrity_error(
                exc,
                "update",
                {"id": obj_id, "payload": sorted(data.keys())},
            ) from exc
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise InfrastructureDatabaseError(
                message=f"Failed to update {self.model.__name__}",
                entity=self.model.__name__,
                operation="update",
                details={
                    "id": obj_id,
                    "payload": sorted(data.keys()),
                    "db_error": str(exc),
                },
            ) from exc
        return obj

    def delete(self, obj_id: int) -> None:
        obj = self.get(obj_id)
        self.db.delete(obj)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise self._map_integrity_error(exc, "delete", {"id": obj_id}) from exc
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise InfrastructureDatabaseError(
                message=f"Failed to delete {self.model.__name__}",
                entity=self.model.__name__,
                operation="delete",
                details={"id": obj_id, "db_error": str(exc)},
            ) from exc

    def _map_integrity_error(
        self,
        exc: IntegrityError,
        operation: str,
        details: dict,
    ) -> InfrastructureIntegrityError:
        original_error = str(exc.orig).lower()

        if (
            "unique constraint failed" in original_error
            or "duplicate key value violates unique constraint" in original_error
        ):
            return InfrastructureConflictError(
                message=f"{self.model.__name__} conflicts with existing data",
                entity=self.model.__name__,
                operation=operation,
                details={**details, "db_error": str(exc.orig)},
            )

        if (
            "foreign key constraint failed" in original_error
            or "violates foreign key constraint" in original_error
        ):
            return InfrastructureIntegrityError(
                message=f"{self.model.__name__} contains invalid related object references",
                entity=self.model.__name__,
                operation=operation,
                details={**details, "db_error": str(exc.orig)},
            )

        return InfrastructureIntegrityError(
            message=f"{self.model.__name__} contains invalid data",
            entity=self.model.__name__,
            operation=operation,
            details={**details, "db_error": str(exc.orig)},
        )
