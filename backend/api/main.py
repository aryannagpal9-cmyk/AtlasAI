from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from shared.logging import setup_logger
from shared.config import settings

# Import Routers
from api.routers import health, stream, clients, risks, meetings, drafts, chat, tasks

logger = setup_logger("api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Atlas API starting up...")
    yield
    logger.info("Atlas API shutting down...")

app = FastAPI(title="Atlas Zero API", lifespan=lifespan)

# CORS
raw_origins = settings.cors_origins.split(",")
origins = [o.strip() for o in raw_origins if o.strip()]
logger.info(f"Configuring CORS with allowed origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception at {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred.", "detail": str(exc) if settings.debug else None},
    )

# Include Routers
app.include_router(health.router, tags=["System"])
app.include_router(stream.router, tags=["Intelligence Stream"])
app.include_router(clients.router, tags=["Clients"])
app.include_router(risks.router, tags=["Risk Events"])
app.include_router(meetings.router, tags=["Meetings"])
app.include_router(drafts.router, tags=["Draft Actions"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(tasks.router, tags=["Background Tasks"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
