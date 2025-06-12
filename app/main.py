# -*- coding: utf-8 -*-
"""
Main application file for the Amplify AI FastAPI service.

This file initializes the FastAPI application, configures middleware (like CORS),
includes the API routers from other modules, and defines global application-level
logic like startup and shutdown events. It serves as the primary entry point for
the web server (Uvicorn).
"""

# =======================================================================
#  1. APPLICATION ENTRY POINT (MAIN) - Amplify AI
# =======================================================================

# -----------------------------------------------------------------------
#  IMPORTS
# -----------------------------------------------------------------------

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Internal imports
from app.config import settings
from app.endpoints import router as api_router
from app.services import ContentGenerationService # Import the service to pre-load it

# -----------------------------------------------------------------------
#  APPLICATION LIFECYCLE MANAGEMENT
# -----------------------------------------------------------------------

# By creating the service instance here at the module level,
# we ensure its __init__ method (which loads all heavy models) is run
# only once when the application starts up. This is a clean and effective
# way to manage the application's state.
content_generation_service = ContentGenerationService()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for generating multimodal social media content using an advanced RAG pipeline with LangChain.",
    version="1.0.0",
    contact={
        "name": "Daniel Moreno",
        "url": "https://www.linkedin.com/in/dmoreno-ai/",
        "email": "danielmoreno3291@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# -----------------------------------------------------------------------
#  MIDDLEWARE CONFIGURATION
# -----------------------------------------------------------------------

# Configure CORS (Cross-Origin Resource Sharing) middleware
# This is essential to allow the Streamlit frontend (running on a different port)
# to communicate with this FastAPI backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------
#  API ROUTER INCLUSION
# -----------------------------------------------------------------------

# Include the router from endpoints.py with a versioned prefix.
app.include_router(api_router, prefix="/api/v1")

# -----------------------------------------------------------------------
#  ROOT ENDPOINT & LIFESPAN EVENTS
# -----------------------------------------------------------------------

@app.on_event("startup")
def on_startup():
    """
    This function runs when the application starts.
    We use it to confirm that the model loading (triggered by the service
    instantiation above) is complete.
    """
    print("--- Amplify AI Application Startup ---")
    print(f"Project: {settings.PROJECT_NAME}")
    print("API is now ready to accept requests.")
    print("Navigate to http://localhost:8000/docs for API documentation.")
    print("---")


@app.on_event("shutdown")
def on_shutdown():
    """
    This function runs when the application is shutting down.
    It's a good place to clean up resources if needed.
    """
    print("--- Amplify AI Application Shutting Down ---")


@app.get("/", tags=["Root"])
async def read_root():
    """A simple root endpoint to confirm that the API is running."""
    return {"message": f"Welcome to the {settings.PROJECT_NAME} API. Visit /docs for details."}