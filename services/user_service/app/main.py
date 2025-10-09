# app/main.py

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt

from . import crud, models, schemas, security
from .database import SessionLocal, engine

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

# --- FastAPI 应用元数据 ---
# 为我们的API文档添加标题、描述和版本信息
app = FastAPI(
    title="U分U享 - 用户认证微服务",
    description="""
    这是"U分U享"项目的核心用户认证服务，提供用户注册、登录和身份验证功能。🚀

    **主要功能**:
    * **用户注册** (`/users/`)
    * **用户登录获取Token** (`/token`)
    * **获取当前用户信息** (`/users/me/`)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# --- 依赖项 ---
def get_db():
    """每个请求的数据库会话依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """解析Token，获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# --- API Endpoints ---

@app.post("/users/", response_model=schemas.User, tags=["Users"], summary="注册新用户")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    创建一个新用户并将其存储在数据库中。

    - **username**: 必须是唯一的，不能重复注册。
    - **password**: 将被哈希加密后存储。
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token, tags=["Users"], summary="用户登录获取访问令牌")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    使用用户名和密码通过OAuth2的密码流(password flow)进行验证，成功后返回一个JWT访问令牌。
    """
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.User, tags=["Users"], summary="获取当前用户信息")
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    一个需要有效JWT令牌才能访问的受保护接口。

    它会解析请求头中的Bearer Token，验证其有效性，并返回对应的用户信息。
    """
    return current_user
