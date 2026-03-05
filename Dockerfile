# 1. 使用国内加速的 Python 3.11 基础镜像
FROM registry.cn-hangzhou.aliyuncs.com/library/python:3.11-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 安装系统级依赖 (关键：必须包含 tesseract 中文语言包)
# 移除 nginx，只保留 OCR 和 OpenCV 所需的库
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/* \
    && tesseract --list-langs # 验证语言包是否安装成功

# 4. 配置 pip 国内镜像加速
ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
ENV PIP_TRUSTED_HOST=mirrors.aliyun.com

# 5. 先复制依赖文件并安装 (利用缓存层)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. 复制项目所有代码
COPY . .

# 7. 创建必要的运行目录 (上传文件和数据库)
RUN mkdir -p /app/data/uploads /app/data/chroma_db

# 8. 设置环境变量 (可选，用于指定配置文件路径等)
ENV PYTHONPATH=/app

# 9. 暴露端口 (FastAPI 默认 8000)
EXPOSE 8000

# 10. 【核心修改】直接使用 uvicorn 启动，不再依赖 start.sh 和 nginx
# 格式：uvicorn <模块路径>:<变量名> --host 0.0.0.0 --port 8000
# 根据你的 main.py，模块是 app.main，变量是 app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]