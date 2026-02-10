from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# Load environment variables from .env  file
load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
assert SECRET_KEY is not None, "SECRET_KEY environment variable is not set"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class JwtHandler:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        # Truncate password to 72 bytes as required by bcrypt
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            password = password_bytes[:72].decode("utf-8", errors="ignore")
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # type: ignore
        return encoded_jwt

    @staticmethod
    def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
        try:
            payload = jwt.decode(
                credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]  # type: ignore
            )
            username = payload.get("sub")
            role = payload.get("role")

            if username is None or role is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            return {"username": username, "role": role}

        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    @staticmethod
    def get_current_user(data_user: dict = Depends(verify_token)):
        return data_user.get("username")

    @staticmethod
    def get_current_user_role(data_user: dict = Depends(verify_token)):
        return data_user.get("role")
