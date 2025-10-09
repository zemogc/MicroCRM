from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: Exception):
    """Handle general HTTP exceptions"""
    logger.error(f"HTTP error: {str(exc)}")
    return JSONResponse(
        status_code=getattr(exc, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR),
        content={
            "error": exc.__class__.__name__,
            "detail": str(exc),
            "path": str(request.url)
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors (422)"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Validation error on {request.url}: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "detail": "Invalid request data",
            "errors": errors,
            "path": str(request.url)
        }
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    logger.error(f"Database error on {request.url}: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "DatabaseError",
            "detail": "An error occurred while processing your request",
            "path": str(request.url)
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unexpected error on {request.url}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "detail": "An unexpected error occurred",
            "path": str(request.url)
        }
    )

def sanitize_error_message(message: str) -> str:
    """
    Sanitize error messages to avoid exposing sensitive information.
    Remove any potential SQL, file paths, or sensitive data.
    """
    sensitive_keywords = [
        "password", "secret", "token", "api_key", "private",
        "database", "connection", "mysql", "localhost"
    ]
    
    message_lower = message.lower()
    for keyword in sensitive_keywords:
        if keyword in message_lower:
            return "An error occurred while processing your request"
    
    return message

