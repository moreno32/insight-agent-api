# -*- coding: utf-8 -*-
# =======================================================================
#  2. API SECURITY
# =======================================================================
#
# Purpose:
#   - Define the security scheme for the API (API Key in 'X-API-KEY' header).
#   - Create a reusable FastAPI dependency to protect endpoints.
#   - This function acts as a "guard" for routes that require authentication.
#
# =======================================================================
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config import settings

# --- Part A: Define WHERE to look for the API key ---
# Create an object that tells FastAPI: "Look for the key
# in an HTTP header named 'X-API-KEY'".
# APIKeyHeader is a helper class from FastAPI for this purpose.
api_key_header_scheme = APIKeyHeader(name="X-API-KEY", auto_error=False)

# --- Part B: Define the guard's LOGIC ---
# This is our dependency function. This is the guard!
def get_api_key(api_key_header: str = Security(api_key_header_scheme)):
    """
    This function is a FastAPI "Dependency".
    1. FastAPI will execute it automatically for protected endpoints.
    2. It will try to extract the value from the 'X-API-KEY' header
       (thanks to `Security(api_key_header_scheme)`).
    3. It will pass that value to the 'api_key_header' parameter.
    """
    # Check if the key was provided and if it matches our secret key.
    if api_key_header == settings.API_SECRET_KEY:
        # If they match, validation is successful.
        # Return the key, and FastAPI proceeds with the request.
        return api_key_header
    else:
        # If they don't match (or if the header is missing), raise an error.
        # HTTPException stops everything immediately and sends an error response.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, # "Unauthorized" status
            detail="Invalid or missing API Key", # Message for the client
        )