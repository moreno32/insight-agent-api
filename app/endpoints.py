# -*- coding: utf-8 -*-
"""
API Endpoints for the Amplify AI project.

This module defines the API routes using FastAPI's APIRouter.
It handles incoming requests, validates them, and calls the appropriate
service functions to perform the core logic.
"""
# =======================================================================
#  4. API ROUTING (ENDPOINTS) - Amplify AI
# =======================================================================

# -----------------------------------------------------------------------
#  IMPORTS
# -----------------------------------------------------------------------

from typing import List

from fastapi import (APIRouter, Depends, File, Form, HTTPException,
                     UploadFile, status)

# Internal imports
from .schemas import ContentGenerationOutput, Msg
from .services import ContentGenerationService

# -----------------------------------------------------------------------
#  DEPENDENCY INJECTION SETUP
# -----------------------------------------------------------------------

# By creating the service instance here, we ensure it's a singleton.
# The __init__ method (which loads all heavy models) is run only once
# when the application starts, not on every request.
content_generation_service = ContentGenerationService()

def get_content_generation_service() -> ContentGenerationService:
    """Dependency function to get the shared service instance."""
    return content_generation_service

# -----------------------------------------------------------------------
#  ROUTER DEFINITION
# -----------------------------------------------------------------------

router = APIRouter()

# =======================================================================
#  API ENDPOINTS
# =======================================================================

@router.get(
    "/health",
    response_model=Msg,
    tags=["Monitoring"],
    summary="Check API Health",
    description="A simple endpoint to verify that the service is running and responsive."
)
async def health_check():
    """Returns a simple success message if the service is alive."""
    return {"message": "Amplify AI service is running smoothly!"}


@router.post(
    "/generate",
    response_model=ContentGenerationOutput,
    status_code=status.HTTP_201_CREATED,
    tags=["Content Generation"],
    summary="Generate Multimodal Social Media Content",
    description="This is the main endpoint. It accepts a user prompt, a brand guide, and style images to generate a complete social media post (text + image)."
)
async def generate_content(
    # The service instance is injected by FastAPI's dependency system
    service: ContentGenerationService = Depends(get_content_generation_service),
    
    # Inputs are defined here using Form() and File() for multipart/form-data
    user_prompt: str = Form(
        ...,
        description="The user's core request, e.g., 'Announce our new fall coffee'."
    ),
    brand_guide_file: UploadFile = File(
        ...,
        description="The user's brand guide in .md format."
    ),
    style_images: List[UploadFile] = File(
        ...,
        description="A list of images that represent the brand's visual style."
    )
):
    """
    Orchestrates the full content generation pipeline.

    - **Receives** user inputs as multipart form data.
    - **Delegates** the complex generation logic to the ContentGenerationService.
    - **Handles** potential errors and returns a structured response.
    """
    try:
        # Call the main orchestrator method from the service
        result = await service.create_post_pipeline(
            user_prompt=user_prompt,
            brand_guide_file=brand_guide_file,
            style_images=style_images
        )
        return result
    except Exception as e:
        # A robust error handling block.
        # In a real production scenario, you would log the full exception trace.
        print(f"[ERROR] An unhandled exception occurred in the generation pipeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while generating content. Please check the server logs for more details."
        )