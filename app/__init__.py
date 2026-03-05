from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, study

def create_app() -> FastAPI:
    """创建并配置FastAPI应用"""
    app = FastAPI(
        title="个性化学习Agent",
        description="为初高中学生定制的AI学习助手",
        version="1.0.0"
    )

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(auth.router, prefix="/auth", tags=["认证"])
    app.include_router(study.router, prefix="/study", tags=["学习"])

    # 根路径
    @app.get("/")
    async def root():
        return {"message": "个性化学习Agent服务已启动", "version": "1.0.0"}

    return app
