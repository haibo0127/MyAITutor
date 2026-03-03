"""
SQLAlchemy数据模型
定义：用户、用户记忆
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


# ===================== 用户模型 =====================
class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    grade = Column(String(20), nullable=False)  # 初中/高中/admin
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ===================== 用户记忆模型 =====================
class UserMemory(Base):
    """用户记忆表（个性化学习数据）"""
    __tablename__ = "user_memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    memory_key = Column(String(100), nullable=False)  # 如：weak_points_junior
    memory_value = Column(Text, nullable=False)  # JSON字符串存储
    confidence = Column(Integer, default=80)  # 置信度（0-100）
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 修复联合唯一索引（解决SAWarning）
    __table_args__ = (
        UniqueConstraint("user_id", "memory_key", name="unique_user_memory_key"),
    )