"""
Pydantic数据验证模型（适配Pydantic V2）
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any

# ===================== 令牌相关模型 =====================
class Token(BaseModel):
    """登录返回的令牌模型"""
    access_token: str
    token_type: str
    user_info: Optional[dict] = None

class TokenData(BaseModel):
    """令牌解析后的用户数据"""
    username: Optional[str] = None

# ===================== 用户相关模型 =====================
class UserBase(BaseModel):
    """用户基础模型（共用字段）"""
    username: str = Field(min_length=3, max_length=50, description="用户名（唯一）")
    full_name: str = Field(min_length=1, max_length=100, description="真实姓名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    grade: str = Field(pattern="^(初中|高中|admin)$", description="年级/角色：初中/高中/admin")
    is_active: Optional[bool] = Field(True, description="是否激活")

class UserCreate(UserBase):
    """用户注册请求模型"""
    password: str = Field(min_length=6, max_length=72, description="密码（6-72位）")

class UserUpdate(BaseModel):
    """用户信息更新模型"""
    full_name: Optional[str] = Field(None, description="真实姓名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    grade: Optional[str] = Field(None, pattern="^(初中|高中|admin)$", description="年级/角色")
    is_active: Optional[bool] = Field(None, description="是否激活")

class UserResponse(UserBase):
    """用户响应模型（返回给前端）"""
    id: int
    is_admin: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    # Pydantic V2适配：orm_mode → from_attributes
    class Config:
        from_attributes = True

# ===================== 学习记忆相关模型 =====================
class MemoryCreate(BaseModel):
    """记忆创建模型（兼容旧命名）"""
    memory_key: str = Field(description="记忆键（如：weak_points_junior）")
    memory_value: str = Field(description="记忆值（JSON字符串）")
    confidence: Optional[float] = Field(0.8, description="置信度（0-1）")

class UserMemoryCreate(MemoryCreate):
    """用户记忆创建模型（匹配memory_manager.py的导入）"""
    user_id: Optional[int] = Field(None, description="用户ID")

class MemoryResponse(BaseModel):
    """记忆响应模型"""
    id: int
    user_id: int
    memory_key: str
    memory_value: str
    confidence: float
    updated_at: str

    # Pydantic V2适配
    class Config:
        from_attributes = True

# ===================== 图片上传/分析相关模型 =====================
class UploadResponse(BaseModel):
    """图片上传响应模型"""
    status: str
    detail: str
    file_id: str
    file_path: str
    user_id: int

class AnalysisResponse(BaseModel):
    """图片分析响应模型"""
    status: str
    user_info: dict
    analysis: dict