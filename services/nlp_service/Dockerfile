# -------- Stage 1: 获取静态 ffmpeg 二进制（已编译好，省去 apt 下载） --------
FROM jrottenberg/ffmpeg:7-scratch AS ffmpeg-static

# -------- Stage 2: 应用运行环境（Python + FastAPI） ------------------------
FROM python:3.11-alpine

# 安装 ffmpeg 及常用工具
RUN apk add --no-cache ffmpeg grep

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝应用代码和环境变量
COPY app /code/app
COPY .env /code/.env

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
