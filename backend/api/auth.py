"""
api/auth.py — Authentication endpoints.

Handles user registration and login.
Uses JWT (JSON Web Tokens) — think of it as a digital ID card.
When you log in, you get a token. You send that token with every request
to prove who you are.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

from database import get_db
from models import User

load_dotenv()

router = APIRouter()

# Password hashing — converts "mypassword" into a scrambled string
# so even if the database is hacked, passwords are safe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme — tells FastAPI how to extract the JWT token from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


# ── Pydantic Models (request/response shapes) ─────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr      # Validates that it's a real email format
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


# ── Helper Functions ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Convert plain text password to a secure hash."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if the entered password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Create a JWT token containing user info, expires in TOKEN_EXPIRE_MINUTES."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    FastAPI dependency — extracts the current user from the JWT token.
    Add to any route to require login: current_user = Depends(get_current_user)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register", status_code=201)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new analyst account."""
    # Check if email is already taken
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create user with hashed password
    user = User(
        email=request.email,
        username=request.username,
        hashed_password=hash_password(request.password)
    )
    db.add(user)
    db.commit()
    return {"message": "Account created successfully", "username": user.username}


@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Log in and receive a JWT token."""
    # OAuth2PasswordRequestForm expects "username" field — we'll use email
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token(data={"sub": user.id})
    return LoginResponse(access_token=token, username=user.username)


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the current logged-in user's info."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
    }
