# 使用官方的 Python 3.11 镜像作为基础
FROM python:3.11-slim

# 在容器内创建一个工作目录
WORKDIR /usr/src/app

# 安装基础依赖和SQL Server ODBC驱动
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
        unixodbc \
        unixodbc-dev && \
    # 添加 Microsoft 的 GPG 密钥
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
    # 添加 Microsoft 软件源
    echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list && \
    # 更新软件包列表并安装 SQL Server ODBC 驱动
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    # 清理缓存
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件到工作目录
COPY ./requirements.txt .

# 安装 Python 依赖库
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个 app 目录到工作目录
COPY ./app ./app

# 容器启动时要执行的命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]