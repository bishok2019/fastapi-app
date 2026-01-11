from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apps.database import get_db
from base.pagination import paginate
from base.route import StandardResponse

from .models import APILog, ErrorLog
from .schemas import APILogList, APILogRetrieve, ErrorLogList, ErrorLogRetrieve

router = APIRouter()


@router.get("/list", response_model=StandardResponse)
def list_api_logs(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    """List all API logs"""
    result = paginate(
        query=db.query(APILog).order_by(APILog.created_at.desc()),
        page=page,
        page_size=page_size,
        schema=APILogList,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=StandardResponse.success_response(
            data=result.data,
            message="API logs fetched successfully.",
            meta=result.meta,
        ).model_dump(mode="json"),
    )


@router.get("/retrieve/{log_id}", response_model=StandardResponse)
def retrieve_api_logs(
    log_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve a specific API log by ID"""
    result = db.query(APILog).filter(APILog.id == log_id).first()
    if not result:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=StandardResponse.error_response(
                message="API log not found.",
            ).model_dump(),
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=StandardResponse.success_response(
            data=APILogRetrieve.model_validate(result),
            message="API logs retrieved successfully.",
            # meta=result.meta,
        ).model_dump(),
    )


@router.get("/error-logs", response_model=StandardResponse)
def list_error_logs(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    """List all error logs"""
    result = paginate(
        query=db.query(ErrorLog).order_by(ErrorLog.created_at.desc()),
        page=page,
        page_size=page_size,
        schema=ErrorLogList,
    )
    if not result.data:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=StandardResponse.error_response(
                message="No error logs found.",
            ).model_dump(),
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=StandardResponse.success_response(
            data=result.data,
            message="Error logs fetched successfully.",
            # meta=result.meta,
        ).model_dump(mode="json"),
    )


@router.get("/error-logs/{log_id}", response_model=StandardResponse)
def retrieve_error_log(
    log_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve a specific error log by ID"""
    result = db.query(ErrorLog).filter(ErrorLog.id == log_id).first()
    if not result:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=StandardResponse.error_response(
                message="Error log not found.",
            ).model_dump(),
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=StandardResponse.success_response(
            data=ErrorLogRetrieve.model_validate(result),
            message="Error log retrieved successfully.",
        ).model_dump(mode="json"),
    )
