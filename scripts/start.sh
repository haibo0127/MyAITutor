#!/bin/bash

# 初始化管理员
python scripts/init_admin.py

# 启动Nginx
nginx

# 启动FastAPI应用
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4