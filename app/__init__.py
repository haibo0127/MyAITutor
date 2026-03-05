from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, study
# 1. 导入离线文档插件
from fastapi_offline_docs import add_offline_docs

def create_app() -> FastAPI:
    """创建并配置FastAPI应用"""
    app = FastAPI(
        title="个性化学习Agent",
        description="为初高中学生定制的AI学习助手",
        version="1.0.0"
    )

    # 2. 启用离线文档支持 (关键步骤)
    # 这会将 Swagger UI 的资源打包在本地，不再依赖外部 CDN
    add_offline_docs(app)

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
