"""
个性化学习Agent - 主入口文件
适配结构：routers/ + agents/ + utils/
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# 本地模块导入
from app.config import settings
from app.database import engine, Base
from app.routers import auth, study

# ===================== 初始化 =====================
# 创建数据库表（首次启动自动创建）
Base.metadata.create_all(bind=engine)

# 创建FastAPI实例
app = FastAPI(
    title="个性化学习Agent",
    description="面向中小学生的AI学习助手，支持拍照批改、错题分析、个性化记忆",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ===================== 中间件 =====================
# 跨域配置（本地测试允许所有来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080"],  # 仅允许前端服务地址
    allow_credentials=True,                   # 允许携带Cookie/Token
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # 明确允许的方法
    allow_headers=["*"],                      # 允许所有请求头
)

# 静态文件挂载（上传的图片）
os.makedirs(settings.upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# ===================== 路由注册 =====================
app.include_router(auth.router, prefix="/auth", tags=["认证模块"])
app.include_router(study.router, prefix="/study", tags=["学习模块"])

# ===================== 健康检查 =====================
@app.get("/", summary="服务健康检查")
async def root():
    return JSONResponse(
        content={
            "status": "success",
            "message": "个性化学习Agent服务已启动",
            "version": "1.0.0",
            "docs": "/docs",
            "data_dir": settings.upload_dir
        }
    )

# ===================== 全局异常处理 =====================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常捕获"""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "detail": f"服务器内部错误: {str(exc)}",
            "request_url": str(request.url)
        }
    )

# ===================== 本地启动 =====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        reload_dirs=["app"]
    )