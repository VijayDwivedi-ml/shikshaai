from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
import time

from schemas import TeachingRequest, AgentResponse
from agent import TeachingResourceAgent
from config import settings, Settings
from logger import logger

# Global agent instance
_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async application lifespan for startup/shutdown"""
    global _agent
    
    # Startup
    logger.info("Starting Teaching Agent API")
    
    # Validate settings
    try:
        settings.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise
    
    # Initialize agent
    _agent = TeachingResourceAgent()
    
    # Run async health check
    health = await _agent.health_check()
    logger.info(f"Agent health check: {health}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Teaching Agent API")
    # Cleanup if needed

# Create FastAPI app
app = FastAPI(
    title="Teaching Resource Agent API",
    description="Async AI agent for discovering teaching resources using Gemini",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get agent
async def get_agent():
    if _agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return _agent

# Middleware for logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log request
    logger.info(
        f"Request processed",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "duration": f"{duration:.3f}s",
            "client": request.client.host if request.client else "unknown"
        }
    )
    
    # Add performance headers
    response.headers["X-Processing-Time"] = str(duration)
    
    return response

# Routes
@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "service": "Teaching Resource Agent",
        "version": "1.0.0",
        "status": "operational",
        "agent": _agent.name if _agent else "not initialized",
        "endpoints": {
            "GET /health": "Agent health check",
            "POST /find-resources": "Find teaching resources",
            "GET /": "This information"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check(agent: TeachingResourceAgent = Depends(get_agent)):
    """Async health check endpoint"""
    health_data = await agent.health_check()
    status_code = 200 if health_data.get("status") == "healthy" else 503
    return JSONResponse(content=health_data, status_code=status_code)

@app.post("/find-resources", response_model=AgentResponse)
async def find_resources(
    request: TeachingRequest,
    agent: TeachingResourceAgent = Depends(get_agent)
):
    """
    Main endpoint for finding teaching resources
    
    Example request:
    ```json
    {
        "topic": "photosynthesis",
        "grade": "7",
        "constraints": ["hands-on", "low-cost"],
        "max_resources": 3
    }
    ```
    """
    logger.info(
        f"Received resource request",
        extra={
            "topic": request.topic,
            "grade": request.grade,
            "constraints": request.constraints,
            "max_resources": request.max_resources
        }
    )
    
    try:
        # Run agent asynchronously
        response = await agent.run(request)
        return response
        
    except Exception as e:
        logger.error(f"Endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Agent processing error: {str(e)}"
        )

@app.get("/metrics")
async def metrics(agent: TeachingResourceAgent = Depends(get_agent)):
    """Simple metrics endpoint (could be enhanced with Prometheus)"""
    return {
        "agent": agent.name,
        "version": agent.version,
        "gemini_api_key_set": bool(settings.GEMINI_API_KEY),
        "max_concurrent_tasks": settings.MAX_CONCURRENT_TASKS,
        "use_cache": settings.USE_CACHE,
        "timestamp": datetime.now().isoformat()
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# Server entry point
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level=settings.LOG_LEVEL.lower(),
        timeout_keep_alive=settings.REQUEST_TIMEOUT
    )