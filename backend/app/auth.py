# backend/app/auth.py
import os
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from typing import Optional

from .database import get_user_by_email, create_user
from .models import User

load_dotenv()

# Allow insecure transport for local development (HTTP instead of HTTPS)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

router = APIRouter()

# --- JWT Configuration ---
SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Dependency to get current user ---
async def get_current_user(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- Google OAuth Configuration ---
REDIRECT_URI = "http://localhost:8000/auth/callback"

# The flow will fail gracefully if client_secret.json is not present
try:
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=[
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid"
        ],
        redirect_uri=REDIRECT_URI
    )
except FileNotFoundError:
    flow = None

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.get("/login")
async def login():
    if not flow:
        raise HTTPException(status_code=500, detail="OAuth is not configured. Missing client_secret.json.")
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return RedirectResponse(authorization_url)

@router.get("/callback")
async def auth_callback(request: Request):
    if not flow:
        raise HTTPException(status_code=500, detail="OAuth is not configured.")
    
    # Use the full URL for the fetch_token method
    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials

    token_request = google_requests.Request()
    id_info = id_token.verify_oauth2_token(
        id_token=credentials.id_token,
        request=token_request,
        audience=credentials.client_id
    )

    email = id_info.get("email")
    full_name = id_info.get("name")
    google_id = id_info.get("sub")

    user = await get_user_by_email(email)
    if not user:
        new_user_data = User(
            email=email,
            full_name=full_name,
            google_id=google_id
        )
        await create_user(new_user_data.dict())

    access_token = create_access_token(data={"sub": email})
    
    # Redirect to frontend dashboard, setting the cookie
    # Try port 5173 first (Vite default), fallback to 5174
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    response = RedirectResponse(url=f"{frontend_url}/home")
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite='lax')
    return response

@router.get("/me")
async def read_users_me(email: str = Depends(get_current_user)):
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return {"email": user["email"], "name": user["full_name"]}

@router.get("/logout")
async def logout():
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    response = RedirectResponse(url=f"{frontend_url}/")
    response.delete_cookie(key="access_token")
    return response
