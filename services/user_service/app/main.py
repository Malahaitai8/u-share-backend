# app/main.py

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt

from . import crud, models, schemas, security
from .database import SessionLocal, engine, MASTER_DATABASE_URL
from sqlalchemy import create_engine as create_sqlalchemy_engine, text

# 创建数据库（如果不存在）
def create_database_if_not_exists():
    try:
        # 先连接到master数据库
        master_engine = create_sqlalchemy_engine(MASTER_DATABASE_URL, connect_args={"timeout": 30})
        with master_engine.connect() as conn:
            # 检查数据库是否存在
            result = conn.execute(text("SELECT name FROM sys.databases WHERE name = 'UFunUShareDB'"))
            if not result.fetchone():
                # 创建数据库
                conn.execute(text("CREATE DATABASE UFunUShareDB"))
                print("数据库 UFunUShareDB 创建成功")
            else:
                print("数据库 UFunUShareDB 已存在")
        master_engine.dispose()
    except Exception as e:
        print(f"创建数据库时出错: {e}")
        # 如果创建失败，继续尝试连接现有数据库

# 创建数据库（如果不存在）
create_database_if_not_exists()

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

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源，生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/stats/my", response_model=schemas.UserStats, tags=["Stats"], summary="获取当前用户统计数据")
async def get_my_stats(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户的分类统计数据"""
    stats = crud.get_user_stats(db, current_user.id)
    return stats


@app.get("/stats/leaderboard", response_model=schemas.LeaderboardInfo, tags=["Stats"], summary="获取排行榜信息")
async def get_leaderboard(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户的排行榜信息（超过多少百分比的用户）"""
    percentile = crud.get_user_rank_percentile(db, current_user.id)
    return {"rank_percentile": percentile}


@app.post("/stats/record", response_model=schemas.ClassificationRecord, tags=["Stats"], summary="添加分类记录")
async def add_classification(
    garbage_type: str,
    recognition_method: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加一条分类记录并获得积分"""
    record = crud.add_classification_record(db, current_user.id, garbage_type, recognition_method, 1)
    return record
