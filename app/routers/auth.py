"""
用户认证路由

提供用户注册、登录、登出、刷新令牌等认证相关功能
"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import re

from app.core.database import get_mongo_db
from pymongo import MongoClient
from bson import ObjectId
import os

router = APIRouter(prefix="/auth", tags=["认证"])

# JWT配置
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天
REFRESH_TOKEN_EXPIRE_DAYS = 30

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2密码模式
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ============================================================
# 数据模型
# ============================================================

class UserRegister(BaseModel):
    """用户注册请求"""
    email: EmailStr = Field(..., description="邮箱")
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$", description="手机号")

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', v):
            raise ValueError('用户名只能包含字母、数字、下划线和中文')
        return v

    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class Token(BaseModel):
    """令牌响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserInfo(BaseModel):
    """用户信息"""
    id: str
    email: str
    username: str
    phone: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserResponse(BaseModel):
    """用户响应"""
    success: bool
    message: str
    data: Optional[UserInfo] = None


class TokenResponse(BaseModel):
    """令牌响应"""
    success: bool
    message: str
    data: Optional[Token] = None


# ============================================================
# 工具函数
# ============================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """加密密码"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """解码令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已过期"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌"
        )


async def get_current_user(token: str = Depends(oauth2_scheme), db: MongoClient = Depends(get_mongo_db)) -> dict:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)

    if payload.get("type") != "access":
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    users_collection = db["tradingagents"]["users"]
    user = await users_collection.find_one({"_id": ObjectId(user_id)})

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """获取当前活跃用户"""
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user


# ============================================================
# 路由端点
# ============================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: MongoClient = Depends(get_mongo_db)):
    """
    用户注册

    - **email**: 邮箱地址（唯一）
    - **username**: 用户名（唯一）
    - **password**: 密码（至少6位，包含字母和数字）
    - **phone**: 手机号（可选）
    """
    users_collection = db["tradingagents"]["users"]

    # 检查邮箱是否已存在
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )

    # 检查用户名是否已存在
    existing_user = await users_collection.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被使用"
        )

    # 创建新用户
    now = datetime.utcnow()
    user_doc = {
        "email": user_data.email,
        "username": user_data.username,
        "phone": user_data.phone,
        "hashed_password": get_password_hash(user_data.password),
        "avatar": None,
        "bio": None,
        "is_active": True,
        "is_verified": False,
        "created_at": now,
        "updated_at": now,
        "last_login": None,
    }

    result = await users_collection.insert_one(user_doc)
    user_id = result.inserted_id

    # 创建用户统计
    await db["tradingagents"]["user_stats"].insert_one({
        "user_id": user_id,
        "guides_count": 0,
        "trips_count": 0,
        "favorites_count": 0,
        "created_at": now,
    })

    # 返回用户信息
    user_doc["id"] = str(user_id)
    del user_doc["hashed_password"]

    return UserResponse(
        success=True,
        message="注册成功",
        data=UserInfo(**user_doc)
    )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: MongoClient = Depends(get_mongo_db)):
    """
    用户登录

    - **username**: 用户名或邮箱
    - **password**: 密码

    返回访问令牌和刷新令牌
    """
    users_collection = db["tradingagents"]["users"]

    # 支持用户名或邮箱登录
    query = {
        "$or": [
            {"username": user_data.username},
            {"email": user_data.username}
        ]
    }

    user = await users_collection.find_one(query)

    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    # 更新最后登录时间
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )

    # 创建令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["_id"])},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(user["_id"])})

    # 保存刷新令牌
    await db["tradingagents"]["refresh_tokens"].insert_one({
        "user_id": user["_id"],
        "token": refresh_token,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "is_revoked": False
    })

    return TokenResponse(
        success=True,
        message="登录成功",
        data=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: MongoClient = Depends(get_mongo_db)):
    """
    刷新访问令牌

    - **refresh_token**: 刷新令牌
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新令牌已过期"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌类型错误"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌"
        )

    # 检查刷新令牌是否有效
    tokens_collection = db["tradingagents"]["refresh_tokens"]
    token_doc = await tokens_collection.find_one({
        "token": refresh_token,
        "is_revoked": False
    })

    if not token_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新令牌已失效"
        )

    # 检查用户是否存在
    users_collection = db["tradingagents"]["users"]
    user = await users_collection.find_one({"_id": ObjectId(user_id)})

    if not user or not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )

    # 创建新的访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["_id"])},
        expires_delta=access_token_expires
    )

    return TokenResponse(
        success=True,
        message="令牌刷新成功",
        data=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    )


@router.post("/logout")
async def logout(
    refresh_token: str,
    current_user: dict = Depends(get_current_active_user),
    db: MongoClient = Depends(get_mongo_db)
):
    """
    用户登出

    - **refresh_token**: 刷新令牌（将失效）
    """
    # 使刷新令牌失效
    await db["tradingagents"]["refresh_tokens"].update_one(
        {"token": refresh_token},
        {"$set": {"is_revoked": True}}
    )

    return {"success": True, "message": "登出成功"}


@router.get("/me", response_model=UserResponse)
async def get_user_info(current_user: dict = Depends(get_current_active_user)):
    """
    获取当前用户信息
    """
    user_doc = current_user.copy()
    user_doc["id"] = str(user_doc["_id"])
    del user_doc["_id"]
    del user_doc["hashed_password"]

    return UserResponse(
        success=True,
        message="获取用户信息成功",
        data=UserInfo(**user_doc)
    )


@router.put("/me", response_model=UserResponse)
async def update_user_info(
    email: Optional[EmailStr] = None,
    phone: Optional[str] = None,
    bio: Optional[str] = None,
    avatar: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: MongoClient = Depends(get_mongo_db)
):
    """
    更新用户信息

    - **email**: 新邮箱
    - **phone**: 新手机号
    - **bio**: 个人简介
    - **avatar**: 头像URL
    """
    users_collection = db["tradingagents"]["users"]

    # 构建更新数据
    update_data = {"updated_at": datetime.utcnow()}

    if email is not None and email != current_user.get("email"):
        # 检查邮箱是否已被使用
        existing = await users_collection.find_one({"email": email})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
        update_data["email"] = email

    if phone is not None:
        update_data["phone"] = phone

    if bio is not None:
        update_data["bio"] = bio

    if avatar is not None:
        update_data["avatar"] = avatar

    # 更新用户信息
    await users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_data}
    )

    # 获取更新后的用户信息
    updated_user = await users_collection.find_one({"_id": current_user["_id"]})
    user_doc = updated_user.copy()
    user_doc["id"] = str(user_doc["_id"])
    del user_doc["_id"]
    del user_doc["hashed_password"]

    return UserResponse(
        success=True,
        message="更新用户信息成功",
        data=UserInfo(**user_doc)
    )


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: dict = Depends(get_current_active_user),
    db: MongoClient = Depends(get_mongo_db)
):
    """
    修改密码

    - **old_password**: 旧密码
    - **new_password**: 新密码（至少6位，包含字母和数字）
    """
    # 验证旧密码
    if not verify_password(old_password, current_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )

    # 验证新密码
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码至少需要6位"
        )

    if not re.search(r'[A-Za-z]', new_password) or not re.search(r'\d', new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码必须包含字母和数字"
        )

    # 更新密码
    users_collection = db["tradingagents"]["users"]
    await users_collection.update_one(
        {"_id": current_user["_id"]},
        {
            "$set": {
                "hashed_password": get_password_hash(new_password),
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {"success": True, "message": "密码修改成功"}


@router.delete("/me")
async def delete_account(
    current_user: dict = Depends(get_current_active_user),
    db: MongoClient = Depends(get_mongo_db)
):
    """
    删除账户

    注意：此操作不可逆
    """
    users_collection = db["tradingagents"]["users"]

    # 软删除：禁用账户
    await users_collection.update_one(
        {"_id": current_user["_id"]},
        {
            "$set": {
                "is_active": False,
                "deleted_at": datetime.utcnow(),
                "email": f"deleted_{current_user['_id']}@deleted.com"
            }
        }
    )

    # 使所有刷新令牌失效
    await db["tradingagents"]["refresh_tokens"].update_many(
        {"user_id": current_user["_id"]},
        {"$set": {"is_revoked": True}}
    )

    return {"success": True, "message": "账户已删除"}
