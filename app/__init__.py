from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import os

# 导入配置和路由
from app.config import settings
from app.routers import auth, study

# 引入离线文档支持 (注意函数名已修正为 enable_offline_docs)
from fastapi_offline_docs import enable_offline_docs

def create_app() -> FastAPI:
    app = FastAPI(
        title="个性化学习Agent",
        description="为初高中学生定制的AI学习助手",
        version="1.0.0"
    )

    # 1. 启用离线文档 (修复之前的 ImportError)
    enable_offline_docs(app)

    # 2. 配置 CORS (允许跨域请求)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 3. 【新增】挂载前端静态文件目录
    # 获取当前文件 (__init__.py) 的父目录的父目录，即项目根目录
    BASE_DIR = Path(__file__).resolve().parent.parent
    FRONTEND_DIR = BASE_DIR / "frontend"

    # 确保 frontend 目录存在
    if FRONTEND_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
    else:
        print(f"⚠️ 警告: 未找到 frontend 目录 ({FRONTEND_DIR})，前端页面将无法访问。")

    # 4. 【新增】设置根路径默认返回 index.html (登录界面)
    @app.get("/")
    async def read_root():
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {"message": "Frontend not found", "error": "index.html missing"}

    # 5. 注册业务路由
    app.include_router(auth.router, prefix="/auth", tags=["认证"])
    app.include_router(study.router, prefix="/study", tags=["学习"])

    return app
