import logging
import uuid

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.services.ml_client import MLServiceError
from app.services.otp_sender import OtpDeliveryError

logger = logging.getLogger("app.errors")


class AppError(HTTPException):
    def __init__(self, status_code: int, code: str, detail: str):
        super().__init__(status_code=status_code, detail={"detail": detail, "code": code})


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", str(uuid.uuid4()))


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        request_id = _request_id(request)
        body = exc.detail
        if isinstance(body, dict):
            payload = {**body, "request_id": request_id}
        else:
            payload = {"detail": str(body), "code": "HTTP_ERROR", "request_id": request_id}
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(MLServiceError)
    async def ml_service_error_handler(request: Request, exc: MLServiceError):
        # Never leak the underlying httpx exception message (connection
        # details, internal hostnames) to clients — log it server-side instead.
        logger.error("ml_service_unavailable request_id=%s error=%s", _request_id(request), exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "The ML service is temporarily unavailable. Please try again shortly.",
                "code": "ML_SERVICE_UNAVAILABLE",
                "request_id": _request_id(request),
            },
        )

    @app.exception_handler(OtpDeliveryError)
    async def otp_delivery_error_handler(request: Request, exc: OtpDeliveryError):
        # Never leak provider response internals, the MSG91 auth key, or a
        # stack trace to the client — log server-side (already scrubbed by
        # the raiser) and return one generic, safe message.
        logger.error("otp_delivery_failed request_id=%s error=%s", _request_id(request), exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "Could not send the verification code right now. Please try again shortly.",
                "code": "OTP_DELIVERY_UNAVAILABLE",
                "request_id": _request_id(request),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Validation failed",
                "code": "VALIDATION_ERROR",
                "errors": exc.errors(),
                "request_id": _request_id(request),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # Never leak internal stack traces / exception details to clients.
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "code": "INTERNAL_ERROR",
                "request_id": _request_id(request),
            },
        )
