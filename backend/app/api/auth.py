# backend/app/api/auth.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId
import random
import string

from app.database import sync_users_collection, sync_database
from app.database import sync_users_collection, sync_database
from app.schemas.user import UserCreate, UserLogin, User, Token, TokenData, UserVerify, UserUpdate, ChangePassword, ForgotPasswordRequest, ResetPasswordRequest
from app.config import settings
from app.email_conf import conf # Import FastMail config
from fastapi_mail import FastMail, MessageSchema
from pydantic import BaseModel
# Request model for OTP verification
router = APIRouter()
class OtpVerifyRequest(BaseModel):
    email: str
    otp: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# MongoDB collection for temporary OTP storage
otp_collection = sync_database.otp_storage

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = sync_users_collection.find_one({"email": token_data.email})
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(current_user = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

@router.post("/register")
async def register(user: UserCreate):
    # Check if user already exists (email or username)
    if sync_users_collection.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    if sync_users_collection.find_one({"username": user.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    # Rate limit: only allow new OTP every 60 seconds
    otp_entry = otp_collection.find_one({"email": user.email})
    if otp_entry and otp_entry["expires_at"] > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="OTP already sent. Please wait before requesting again."
        )
    # Generate OTP and expiry
    otp = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    
    # Store OTP and user data in MongoDB
    otp_doc = {
        "email": user.email,
        "otp": otp,
        "expires_at": expires_at,
        "user_data": user.model_dump()
    }
    otp_collection.update_one(
        {"email": user.email},
        {"$set": otp_doc},
        upsert=True
    )
    
    # DEBUG: Print OTP to console
    print(f"DEBUG: Generated OTP for {user.email}: {otp}")

    # Send OTP email
    try:
        message = MessageSchema(
            subject="Your OTP for Heavy Rainfall Nowcasting Registration",
            recipients=[user.email],
            body=f"Your OTP is: {otp}",
            subtype="html"
        )
        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        print(f"ERROR: Failed to send email to {user.email}. Error: {e}")
        # We continue even if email fails, so user can use console OTP
        
    return {"message": "OTP sent to your email address (check console if email fails)."}

@router.post("/register/verify", response_model=Token)
async def verify_otp_and_register(verification_data: UserVerify):
    # Check if OTP and user data exist
    otp_doc = otp_collection.find_one({"email": verification_data.email})
    
    if not otp_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request or OTP expired"
        )
        
    user_data = otp_doc.get("user_data")
    
    # Check OTP expiry
    if otp_doc["expires_at"] < datetime.utcnow():
        otp_collection.delete_one({"email": verification_data.email})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired. Please register again."
        )
    # Verify OTP
    if otp_doc["otp"] != verification_data.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
    # Validate required fields
    required_fields = ["email", "username", "password", "is_admin"]
    for field in required_fields:
        if field not in user_data or user_data[field] in (None, ""):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{field}' required."
            )
    # Hash password
    hashed_password = get_password_hash(user_data["password"])
    # Create user document
    user_doc = {
        "email": user_data["email"],
        "username": user_data["username"],
        "hashed_password": hashed_password,
        "is_admin": user_data["is_admin"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    try:
        sync_users_collection.insert_one(user_doc)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    # Clean up temporary storage
    otp_collection.delete_one({"email": verification_data.email})
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/verify-otp")

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = sync_users_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user = Depends(get_current_user)):
    # Convert ObjectId to string and prepare response (without hashed_password)
    response_doc = {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "username": current_user["username"],
        "is_admin": current_user["is_admin"],
        "created_at": current_user["created_at"],
        "updated_at": current_user["updated_at"]
    }
    return User(**response_doc)

@router.put("/me", response_model=User)
async def update_user_me(user_update: UserUpdate, current_user = Depends(get_current_user)):
    update_data = {k: v for k, v in user_update.model_dump().items() if v is not None}
    
    if "username" in update_data:
        if sync_users_collection.find_one({"username": update_data["username"]}):
             raise HTTPException(status_code=400, detail="Username already taken")

    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        sync_users_collection.update_one(
            {"_id": current_user["_id"]},
            {"$set": update_data}
        )
        
    # Fetch updated user
    updated_user = sync_users_collection.find_one({"_id": current_user["_id"]})
    response_doc = {
        "id": str(updated_user["_id"]),
        "email": updated_user["email"],
        "username": updated_user["username"],
        "is_admin": updated_user["is_admin"],
        "created_at": updated_user["created_at"],
        "updated_at": updated_user["updated_at"]
    }
    return User(**response_doc)

@router.post("/change-password")
async def change_password(password_data: ChangePassword, current_user = Depends(get_current_user)):
    if not verify_password(password_data.current_password, current_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    new_hashed_password = get_password_hash(password_data.new_password)
    sync_users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"hashed_password": new_hashed_password, "updated_at": datetime.utcnow()}}
    )
    return {"message": "Password updated successfully"}

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    user = sync_users_collection.find_one({"email": request.email})
    if not user:
        # Don't reveal if user exists
        return {"message": "If email exists, an OTP has been sent."}
    
    # Generate OTP
    otp = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    otp_doc = {
        "email": request.email,
        "otp": otp,
        "expires_at": expires_at,
        "type": "reset_password"
    }
    otp_collection.update_one(
        {"email": request.email},
        {"$set": otp_doc},
        upsert=True
    )
    
    # Send Email
    try:
        message = MessageSchema(
            subject="Password Reset OTP",
            recipients=[request.email],
            body=f"Your password reset OTP is: {otp}",
            subtype="html"
        )
        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        print(f"ERROR sending reset email: {e}")
        
    print(f"DEBUG: Reset OTP for {request.email}: {otp}")
    return {"message": "If email exists, an OTP has been sent."}

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    otp_doc = otp_collection.find_one({"email": request.email, "type": "reset_password"})
    if not otp_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
    if otp_doc["expires_at"] < datetime.utcnow():
        otp_collection.delete_one({"email": request.email})
        raise HTTPException(status_code=400, detail="OTP expired")
        
    if otp_doc["otp"] != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    # Update password
    new_hashed_password = get_password_hash(request.new_password)
    sync_users_collection.update_one(
        {"email": request.email},
        {"$set": {"hashed_password": new_hashed_password, "updated_at": datetime.utcnow()}}
    )
    
    otp_collection.delete_one({"email": request.email})
    return {"message": "Password reset successfully"} 