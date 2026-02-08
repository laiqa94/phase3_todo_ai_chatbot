"""
Main FastAPI application for AI Todo Chatbot
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.chat_endpoint import router as chat_router
from .database.engine import create_db_and_tables
from .config import config


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title=config.PROJECT_NAME,
        version="0.1.0",
        description="AI Todo Chatbot with Cohere integration"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, configure specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(chat_router, prefix="/api/v1")

    # Create database tables on startup
    @app.on_event("startup")
    def on_startup():
        create_db_and_tables()

    # Health check endpoint
    @app.get("/health")
    def health_check():
        return {"status": "healthy", "service": "AI Todo Chatbot"}

    return app


# Create the main application instance
app = create_app()


# Additional utility endpoints
@app.get("/")
def root():
    return {
        "message": "Welcome to AI Todo Chatbot API",
        "version": "0.1.0",
        "endpoints": [
            "GET /health - Health check",
            "POST /api/v1/{user_id}/chat - Chat with AI assistant",
            "POST /api/v1/{user_id}/new_conversation - Start new conversation"
        ]
    }