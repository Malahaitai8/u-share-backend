# app/schemas.py

from pydantic import BaseModel, Field
from typing import Optional

# --- Token Schemas ---
# 定义了Token的响应格式
class Token(BaseModel):
    access_token: str
    token_type: str

# 定义了Token中存储的数据内容
class TokenData(BaseModel):
    username: Optional[str] = None


# --- User Schemas ---
# 用户模型的基础类，包含通用字段
class UserBase(BaseModel):
    username: str

# 用于创建用户的模型，继承自UserBase，并额外包含密码
class UserCreate(UserBase):
    # 使用Field为字段添加额外信息，这些信息会显示在API文档中
    username: str = Field(..., example="newuser123", description="新用户的唯一用户名")
    password: str = Field(..., example="a_strong_password", description="用户的登录密码")

# 从数据库读取并返回给客户端的用户信息模型
class User(UserBase):
    id: int
    username: str = Field(..., example="newuser123")

    class Config:
        # 这个配置项告诉Pydantic模型可以从ORM对象（比如我们的SQLAlchemy模型）中读取数据
        from_attributes = True
