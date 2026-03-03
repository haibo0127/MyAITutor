"""
应用配置加载
兼容OSS/Chroma等额外环境变量，解决Pydantic验证错误
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置模型（兼容所有.env字段）"""
    # ===================== 基础配置 =====================
    env: str = os.getenv("ENV", "development")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", 8000))

    # ===================== 认证配置 =====================
    secret_key: str = os.getenv("SECRET_KEY", "temp_secret_key_1234567890abcdef1234567890abcdef")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 360))

    # ===================== 大模型配置 =====================
    dashscope_api_key: str = os.getenv("DASHSCOPE_API_KEY", "")
    openclaw_api_key: str = os.getenv("OPENCLAW_API_KEY", "")
    use_local_memory: bool = os.getenv("USE_LOCAL_MEMORY", "true").lower() == "true"

    # ===================== 数据库/存储配置 =====================
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/db.sqlite")
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
    chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")  # 新增：兼容.env字段
    upload_dir: str = os.getenv("UPLOAD_DIR", "./data/uploads")

    # ===================== OSS配置（新增，兼容.env字段） =====================
    oss_endpoint: str = os.getenv("OSS_ENDPOINT", "")
    oss_bucket_name: str = os.getenv("OSS_BUCKET_NAME", "")
    oss_access_key_id: str = os.getenv("OSS_ACCESS_KEY_ID", "")
    oss_access_key_secret: str = os.getenv("OSS_ACCESS_KEY_SECRET", "")

    # ===================== 安全配置 =====================
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")

    # 关键：允许额外字段（避免后续新增.env字段报错）
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # 忽略未定义的环境变量，核心修复！
    )


# 全局配置实例
settings = Settings()

# 确保目录存在
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.chroma_db_path, exist_ok=True)
os.makedirs(settings.chroma_persist_dir, exist_ok=True)  # 兼容新增字段