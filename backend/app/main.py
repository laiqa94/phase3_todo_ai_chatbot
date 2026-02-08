from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from .api.v1.api import api_router
from .core.config import settings
print(f"api_router: {api_router}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
print("App created")

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
print("API router included")
print(f"Routes after API: {len(app.routes)}")

# Import and include AI chatbot routes after the main app is set up
# This ensures the same authentication context is used
try:
    import sys
    import os
    # Add the backend directory to sys.path to enable absolute imports
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    from ai_chatbot.api.chat_endpoint import router as chat_router
    app.include_router(chat_router, prefix="/api/v1")
    print("Chat router included")
    print(f"Routes after chat: {len(app.routes)}")
except ImportError as e:
    print(f"Could not import chat router: {e}")
    print("AI Chatbot features will not be available")

# Test endpoint
@app.get("/test")
def test():
    return {"message": "test"}

@app.get("/testchat2")
def test_chat2():
    return {"message": "chat test 2"}

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Todo Backend API",
        "services": [
            "Regular Todo API endpoints via /api/v1/",
            "AI Chatbot endpoints via /api/v1/{user_id}/chat, /api/v1/{user_id}/new_conversation, etc."
        ]
    }

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")