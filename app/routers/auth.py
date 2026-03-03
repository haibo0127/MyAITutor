"""
认证模块路由
包含：登录、注册、修改密码、获取用户信息
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

# 本地模块导入
from app.database import get_db
from app.auth import authenticate_user, create_access_token, get_password_hash, get_current_user
from app.models import User
from app.schemas import UserCreate, UserResponse

# 路由实例
router = APIRouter()


# ------------------- 登录接口 -------------------
@router.post("/token", summary="用户登录获取令牌")
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
) -> dict[str, Any]:
    """
    用户登录接口
    - username: 用户名
    - password: 密码
    """
    # 验证用户
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 生成JWT令牌
    access_token = create_access_token(data={"sub": user.username})

    return {
        "status": "success",
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "grade": user.grade,
            "is_admin": user.is_admin,
            "is_active": user.is_active
        }
    }


# ------------------- 注册接口 -------------------
@router.post("/register", response_model=UserResponse, summary="用户注册")
async def register_user(
        user_in: UserCreate,
        db: Session = Depends(get_db)
) -> Any:
    """
    用户注册接口
    - username: 用户名（唯一）
    - full_name: 真实姓名
    - email: 邮箱（可选）
    - grade: 年级（初中/高中/admin）
    - password: 密码（6-72位）
    """
    # 检查用户名是否已存在
    db_user = db.query(User).filter(User.username == user_in.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在，请更换用户名"
        )

    # 密码哈希（自动截断72字节）
    hashed_password = get_password_hash(user_in.password)

    # 创建新用户
    db_user = User(
        username=user_in.username,
        full_name=user_in.full_name,
        email=user_in.email,
        grade=user_in.grade,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=True if user_in.grade == "admin" else False
    )

    # 保存到数据库
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# ------------------- 获取当前用户信息 -------------------
@router.get("/me", response_model=UserResponse, summary="获取当前登录用户信息")
async def get_current_user_info(
        current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取当前登录用户信息（需携带Bearer令牌）
    """
    return current_user


# ------------------- 修改密码 -------------------
@router.put("/change-password", summary="修改密码")
async def change_password(
        old_password: str,
        new_password: str,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> dict[str, str]:
    """
    修改当前用户密码
    - old_password: 旧密码
    - new_password: 新密码（6-72位）
    """
    # 验证旧密码
    if not authenticate_user(db, current_user.username, old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )

    # 验证新密码长度
    if len(new_password) < 6 or len(new_password) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度必须在6-72位之间"
        )

    # 更新密码
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()

    return {"status": "success", "detail": "密码修改成功，请重新登录"}