# -*- coding: utf-8 -*-
"""
Application Configuration for Amplify AI.

This module uses Pydantic's BaseSettings to load and manage configuration
variables from environment variables and/or a .env file. It centralizes all
application settings into a single, accessible object.

This file is SAFE to commit to Git. Secrets and environment-specific values
should be stored in the .env file.
"""

# =======================================================================
#  1. CONFIGURATION & SETUP - Amplify AI
# =======================================================================

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """
    Main settings for the Amplify AI application.
    
    Reads environment variables from a .env file and validates their types.
    Default values are provided for a standard local development setup.
    """
    # -- Project Metadata --
    PROJECT_NAME: str = "Amplify AI"

    # -- API & Server Settings --
    # List of allowed origins for CORS. Crucial for Streamlit communication.
    ALLOWED_ORIGINS: List[str] = ["http://localhost", "http://localhost:8501"]
    
    # -- API Security --
    # A secret key used to protect endpoints. This should be a long, random
    # string and MUST be set in the .env file for any real deployment.
    API_SECRET_KEY: str = "your_default_secret_key_that_should_be_overridden"
    
    # -- Model Identifiers & Paths --
    
    # 1. Classical ML Model
    CLASSIFIER_MODEL_PATH: str = "models/intent_classifier.pkl"
    
    # 2. Diffusion Model (for image generation)
    DIFFUSION_MODEL_ID: str = "runwayml/stable-diffusion-v1-5"
    
    # 3. Image Captioning Model (for multimodal understanding)
    IMAGE_CAPTION_MODEL_ID: str = "Salesforce/blip-image-captioning-large"
    
    # 4. Embedding Model (for RAG vectorization)
    EMBEDDING_MODEL_NAME: str = "paraphrase-multilingual-mpnet-base-v2"
    
    # -- LangChain & Ollama Configuration --
    
    # Main LLM for high-quality text generation
    LLM_GENERATOR_MODEL: str = "qwen3:8b"
    
    # Faster LLM for retrieval and utility tasks
    LLM_RETRIEVER_MODEL: str = "qwen3:4b"

    class Config:
        """
        Pydantic model configuration.
        - case_sensitive: Ensures that environment variable names match exactly.
        - env_file: Specifies the file to load environment variables from.
        """
        case_sensitive = True
        env_file = ".env"


# Create a single, globally accessible instance of the settings.
# Other modules can import this 'settings' object directly.
settings = Settings()