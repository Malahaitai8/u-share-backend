# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib

# --- 数据库连接配置 ---

# 从你的 docker-compose.yml 文件中获取的数据库连接信息
DB_USERNAME = "sa"
DB_PASSWORD = "Ushare!2025"
DB_SERVER_NAME = "db"  # 开发阶段，从本机连接到Docker暴露的端口
DB_NAME = "UFunUShareDB"
# ODBC 驱动，确保你的 Docker 镜像中包含它
DB_DRIVER = "ODBC Driver 17 for SQL Server"

# 对密码进行 URL 编码，以防密码中有特殊字符导致连接失败
encoded_password = urllib.parse.quote_plus(DB_PASSWORD)

# 构建最终的数据库连接字符串 (Connection String)
SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://{DB_USERNAME}:{encoded_password}@{DB_SERVER_NAME}/{DB_NAME}?driver={DB_DRIVER}"


# --- SQLAlchemy 引擎和会话设置 ---

# 创建 SQLAlchemy 数据库引擎
# connect_args={"timeout": 30} 增加了连接超时，防止网络延迟导致启动失败
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"timeout": 30})

# 创建一个可用于数据库操作的会话 (Session) 类
# autocommit=False: 数据需要手动提交 (db.commit())，更安全
# autoflush=False: 在查询前不会自动将当前更改写入数据库
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建一个声明式基类 (Declarative Base)
# 我们之后创建的所有数据库模型 (ORM classes) 都将继承这个类
Base = declarative_base()
