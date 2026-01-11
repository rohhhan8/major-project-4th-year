# backend/app/auth.py
import os
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel

from .database import get_user_by_email, create_user
from .models import User

load_dotenv()

# Allow insecure transport for local development (HTTP instead of HTTPS)
# WARNING: Do not use this in production environments with real user data.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

router = APIRouter()

# --- JWT Configuration ---
SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Dependency: Get Current User ---
async def get_current_user(request: Request) -> dict:
    """
    Validates the JWT access token and returns the full user document.
    """
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
        
        # Fetch full user details from DB
        user = await get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return user

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- Google OAuth Configuration ---
REDIRECT_URI = "http://localhost:8000/auth/callback"

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
    print("Warning: client_secret.json not found. OAuth will not work.")

def create_access_token(data: dict):
    """
    Creates a new JWT access token with an expiration time.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Password Hashing Config ---
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --- Endpoints ---

@router.post("/signup")
async def register(user_data: UserRegister):
    """
    Registers a new user with email and password.
    """
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    
    new_user = {
        "email": user_data.email,
        "hashed_password": hashed_password,
        "full_name": user_data.full_name,
        "created_at": datetime.now(),
        "provider": "email"
    }
    
    await create_user(new_user)
    
    # Auto-login
    access_token = create_access_token(data={"sub": user_data.email})
    response = JSONResponse({"status": "success", "message": "User created", "user": {"email": user_data.email, "name": user_data.full_name}})
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite='lax')
    return response

@router.post("/login_email")
async def login_email(user_data: UserLogin):
    """
    Authenticates a user using email and password.
    """
    from .database import get_user_by_email_raw
    
    print(f"\n[Auth] 🔐 EMAIL LOGIN ATTEMPT")
    print(f"  - Email: {user_data.email}")
    
    user = await get_user_by_email_raw(user_data.email)
    if not user or not user.get("hashed_password"):
        print(f"  - ❌ User not found or no password set")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
        
    if not verify_password(user_data.password, user["hashed_password"]):
        print(f"  - ❌ Password verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token = create_access_token(data={"sub": user.get("email")})
    
    print(f"  - ✅ Login successful!")
    
    response = JSONResponse({"status": "success", "user": {"email": user["email"], "name": user.get("full_name", "")}})
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite='lax')
    return response

@router.get("/login")
async def login():
    """
    Initiates the Google OAuth 2.0 login flow.
    """
    # ... (Keep existing Google Logic) ...
    if not flow:
        raise HTTPException(status_code=500, detail="OAuth is not configured.")
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return RedirectResponse(authorization_url)

@router.get("/callback")
async def auth_callback(request: Request):
    # ... (Keep existing Google Logic) ...
    # Ensure google_id is saved
    # ...
    # (Rest of existing callback logic)

    if not flow:
        raise HTTPException(status_code=500, detail="OAuth is not configured.")
    
    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials
    token_request = google_requests.Request()
    
    id_info = id_token.verify_oauth2_token(
        id_token=credentials.id_token,
        request=token_request,
        audience=credentials.client_id,
        clock_skew_in_seconds=10
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
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    response = RedirectResponse(url=f"{frontend_url}/home")
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite='lax')
    return response

@router.get("/me")
async def read_users_me(user: dict = Depends(get_current_user)):
    return {"email": user["email"], "name": user["full_name"]}

@router.post("/logout")
@router.get("/logout")
async def logout():
    """Logout user by deleting the access token cookie."""
    response = JSONResponse({"status": "success", "message": "Logged out successfully"})
    response.delete_cookie(key="access_token", path="/", samesite="lax")
    return response

