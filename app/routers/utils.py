from fastapi import HTTPException

from app.errors import DomainError


def raise_http_error(exc: DomainError) -> None:
    raise HTTPException(
        status_code=exc.status_code,
        detail=exc.to_dict(),
    )
