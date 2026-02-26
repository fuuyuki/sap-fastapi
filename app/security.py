from datetime import datetime, timedelta, timezone
from typing import Optional

# security.py
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# Generate a key once and keep it safe (e.g. in environment variable)
# key = Fernet.generate_key()
FERNET_KEY = b"QCp2AHfRD1VSf0bqjQZ8feYXe1i-mDtrBqQ0BgEROyc="
fernet = Fernet(FERNET_KEY)

# --- JWT Config ---
# ⚠️ Replace with a secure random key in production (e.g. openssl rand -hex 32)
SECRET_KEY = "74d611acd59d4a4085c2b097f4a4a9f67be8099158cece9324b598c9c8550904"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# --- Password Hashing ---
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# --- OAuth2 ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login-form")


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with user_id as subject."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {"sub": user_id, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """Extract user_id from JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not isinstance(user_id, str):
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def encrypt_password(password: str) -> str:
    """
    Encrypt a WiFi password using Fernet symmetric encryption.
    Returns a base64-encoded string safe to store in DB.
    """
    token = fernet.encrypt(password.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_password(token: str) -> str:
    """
    Decrypt a previously encrypted WiFi password.
    Returns the original plain text password.
    """
    password = fernet.decrypt(token.encode("utf-8"))
    return password.decode("utf-8")
