import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:
    from ..database.api_operations import APIOperations
except ImportError:
    from database.api_operations import APIOperations

from .routes import articles, sources
from .schemas.common import ErrorResponse

def setup_api_logging():
    """Setup API logging with timestamped file output"""
    # Create organized logs directory structure
    os.makedirs("logs/api", exist_ok=True)
    
    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/api/api_{timestamp}.log"
    
    # Configure logging to write to both file and console
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ],
        force=True  # Override any existing configuration
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"API session started - logging to {log_filename}")
    return log_filename

# Set up API logging
api_log_file = setup_api_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Viaduct Echo API")
    try:
        # Test database connection
        db = APIOperations()
        health = db.health_check()
        if health["status"] == "healthy":
            logger.info(f"Database connected - {health['total_articles']} articles available")
        else:
            logger.error(f"Database connection failed: {health.get('error', 'Unknown error')}")
        db.close()
    except Exception as e:
        logger.error(f"Startup database check failed: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Viaduct Echo API")


# Create FastAPI app
app = FastAPI(
    title="Viaduct Echo API",
    description="REST API for the Viaduct Echo news aggregation system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS for iOS app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled error in {request.method} {request.url}: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred",
            timestamp=datetime.now(),
        ).model_dump(),
    )


# HTTP exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper error response format"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            detail=getattr(exc, "detail", None),
            timestamp=datetime.now(),
        ).model_dump(),
    )


# Health check endpoint
@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Check API and database health",
)
async def health_check():
    """Health check endpoint"""
    try:
        db = APIOperations()
        health_status = db.health_check()
        db.close()

        status_code = (
            status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return JSONResponse(status_code=status_code, content=health_status)

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "database_connected": False,
                "timestamp": datetime.now().isoformat(),
            },
        )


# Root endpoint
@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    description="API information and available endpoints",
)
async def read_root():
    """Root endpoint with API information"""
    return {
        "name": "Viaduct Echo API",
        "version": "1.0.0",
        "description": "REST API for Greater Manchester news aggregation",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "articles": "/api/v1/articles",
            "sources": "/api/v1/sources",
        },
        "timestamp": datetime.now().isoformat(),
    }


# Include routers
app.include_router(articles.router, prefix="/api/v1", tags=["Articles"])
app.include_router(sources.router, prefix="/api/v1", tags=["Sources"])


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests"""
    start_time = datetime.now()

    # Process the request
    response = await call_next(request)

    # Calculate processing time
    process_time = (datetime.now() - start_time).total_seconds()

    # Log the request
    logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.3f}s")

    return response


if __name__ == "__main__":
    import uvicorn

    # Configure uvicorn to use our logging setup
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
                "access": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.FileHandler",
                    "filename": api_log_file,
                },
                "access": {
                    "formatter": "access",
                    "class": "logging.FileHandler", 
                    "filename": api_log_file,
                },
                "console": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["default", "console"], 
                    "level": "INFO",
                    "propagate": False
                },
                "uvicorn.error": {
                    "handlers": ["default", "console"],
                    "level": "INFO", 
                    "propagate": False
                },
                "uvicorn.access": {
                    "handlers": ["access", "console"],
                    "level": "INFO",
                    "propagate": False
                },
                "fastapi": {
                    "handlers": ["default", "console"],
                    "level": "INFO",
                    "propagate": False
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default", "console"]
            }
        }
    )
