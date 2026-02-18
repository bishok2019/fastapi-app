import logging
from datetime import datetime
from math import ceil
from typing import Dict, Generic, List, Optional, Type, TypeVar

from fastapi import HTTPException
from fastapi.params import Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

# logging.basicConfig(
# level=logging.INFO,  # Show INFO and above
# format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
# )
# logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType")
SchemaType = TypeVar("SchemaType")


class PaginationParams(BaseModel):
    page: int
    page_size: int


def get_pagination_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    previous_page: Optional[int]
    next_page: Optional[int]
    timestamp: str


class CustomPagination(BaseModel, Generic[SchemaType]):
    data: List[SchemaType]
    meta: Dict


def paginate(
    *,
    query,
    # page: int = 1,  # assign default page value so we dont have to pass it every time
    # page_size: int = 10,
    pagination: PaginationParams,
    schema: Type[SchemaType],
) -> CustomPagination[SchemaType]:

    page = pagination.page
    page_size = pagination.page_size

    if page < 1:
        raise [HTTPException(status_code=400, detail="page must be >= 1")]
        # raise ValueError("page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise [
            HTTPException(status_code=400, detail="page_size must be between 1 and 100")
        ]
        # raise ValueError("page_size must be between 1 and 100")

    total = query.count()
    total_pages = ceil(total / page_size) if total else 1

    if page > total_pages:
        raise HTTPException(status_code=404, detail="Page not found")
        # raise ValueError("Page not found")

    items = query.offset((page - 1) * page_size).limit(page_size).all()

    serialized_data = [schema.model_validate(item).model_dump() for item in items]

    # logger.info(f"Query: {query}")
    # has_count = hasattr(query, "count")
    # logger.info(f"Has count: {has_count}")
    # logger.info(f"Items: {len(items)}")

    meta = PaginationMeta(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        previous_page=page - 1 if page > 1 else None,
        next_page=page + 1 if page < total_pages else None,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    return CustomPagination(data=serialized_data, meta=meta.model_dump())
