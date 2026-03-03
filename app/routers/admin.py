from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User
from app.auth import get_current_user
from app.schemas import UserLogin  # 复用或新建一个 UserSchema

router = APIRouter(prefix="/admin", tags=["administration"])


@router.get("/users")
def list_users(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    列出所有用户 (仅管理员可用)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view user list."
        )

    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "grade_level": u.grade_level,
            "is_admin": u.is_admin
        }
        for u in users
    ]


@router.post("/reset-password/{target_username}")
def reset_password(
        target_username: str,
        new_password: str,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    管理员重置指定用户的密码
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")

    from app.auth import get_password_hash
    target_user = db.query(User).filter(User.username == target_username).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    target_user.hashed_password = get_password_hash(new_password)
    db.commit()

    return {"message": f"Password for {target_username} has been reset."}