from typing import Generic, TypeVar

from app.errors import (
    DomainConflictError,
    DomainDatabaseError,
    DomainNotFoundError,
    DomainValidationError,
    InfrastructureConflictError,
    InfrastructureDatabaseError,
    InfrastructureError,
    InfrastructureIntegrityError,
    InfrastructureNotFoundError,
)

R = TypeVar("R")


class BaseUseCase(Generic[R]):
    def __init__(self, repository: R, entity_name: str):
        self.repository = repository
        self.entity_name = entity_name

    def list(self):
        try:
            return self.repository.list()
        except InfrastructureError as exc:
            raise self._to_domain_error(exc) from exc

    def get(self, obj_id: int):
        try:
            return self.repository.get(obj_id)
        except InfrastructureError as exc:
            raise self._to_domain_error(
                exc,
                extra_details={"id": obj_id},
            ) from exc

    def create(self, data: dict):
        try:
            return self.repository.create(data)
        except InfrastructureError as exc:
            raise self._to_domain_error(
                exc,
                extra_details={"payload": sorted(data.keys())},
            ) from exc

    def update(self, obj_id: int, data: dict):
        try:
            return self.repository.update(obj_id, data)
        except InfrastructureError as exc:
            raise self._to_domain_error(
                exc,
                extra_details={"id": obj_id, "payload": sorted(data.keys())},
            ) from exc

    def delete(self, obj_id: int) -> None:
        try:
            self.repository.delete(obj_id)
        except InfrastructureError as exc:
            raise self._to_domain_error(
                exc,
                extra_details={"id": obj_id},
            ) from exc

    def _to_domain_error(
        self,
        exc: InfrastructureError,
        extra_details: dict | None = None,
    ):
        details = dict(exc.details)
        if extra_details:
            details.update(extra_details)

        if isinstance(exc, InfrastructureNotFoundError):
            return DomainNotFoundError(
                message=f"{self.entity_name} not found",
                entity=self.entity_name,
                operation=exc.operation,
                details=details,
            )

        if isinstance(exc, InfrastructureConflictError):
            return DomainConflictError(
                message=f"{self.entity_name} conflicts with existing data",
                entity=self.entity_name,
                operation=exc.operation,
                details=details,
            )

        if isinstance(exc, InfrastructureIntegrityError):
            return DomainValidationError(
                message=f"{self.entity_name} contains invalid data",
                entity=self.entity_name,
                operation=exc.operation,
                details=details,
            )

        if isinstance(exc, InfrastructureDatabaseError):
            return DomainDatabaseError(
                message=f"Database error while processing {self.entity_name.lower()}",
                entity=self.entity_name,
                operation=exc.operation,
                details=details,
            )

        return DomainDatabaseError(
            message=f"Unexpected error while processing {self.entity_name.lower()}",
            entity=self.entity_name,
            operation=exc.operation,
            details=details,
        )


class UserUseCase(BaseUseCase):
    def __init__(self, repository):
        super().__init__(repository, "User")


class CategoryUseCase(BaseUseCase):
    def __init__(self, repository):
        super().__init__(repository, "Category")


class LocationUseCase(BaseUseCase):
    def __init__(self, repository):
        super().__init__(repository, "Location")


class PostUseCase(BaseUseCase):
    def __init__(self, repository):
        super().__init__(repository, "Post")


class CommentUseCase(BaseUseCase):
    def __init__(self, repository):
        super().__init__(repository, "Comment")
