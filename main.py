from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pymongo import MongoClient
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, UTC
from bson import ObjectId
from enum import Enum
import os

# Initialize FastAPI app
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["task_manager"]
users_collection = db["users"]
tasks_collection = db["tasks"]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.urandom(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# Enum for task status
class TaskStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

# Pydantic models
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):  # New User model
    id: str
    username: str
    hashed_password: str

class TaskCreate(BaseModel):
    title: str
    description: str
    status: TaskStatus

class TaskUpdate(BaseModel):
    title: str
    description: str
    status: TaskStatus

# Utility functions
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_user(username: str) -> User | None:  # Return User model instead of dict
    user = users_collection.find_one({"username": username})
    if user:
        return User(id=str(user["_id"]), username=user["username"], hashed_password=user["hashed_password"])
    return None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:  # Return User model
    username = decode_access_token(token)
    user = get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

# API Endpoints
@app.post("/api/register")
async def register(user: UserRegister):
    if get_user(user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = get_password_hash(user.password)
    user_dict = {"username": user.username, "hashed_password": hashed_password}
    result = users_collection.insert_one(user_dict)
    return {"id": str(result.inserted_id), "username": user.username}

@app.post("/api/login")
async def login(user: UserLogin):
    db_user = get_user(user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password):  # Use attribute access
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/tasks")
async def get_tasks(current_user: User = Depends(get_current_user)):  # Use User model
    tasks = tasks_collection.find({"user_id": current_user.id})  # Attribute access
    return [
        {"id": str(task["_id"]), "title": task["title"], "description": task["description"], "status": task["status"]}
        for task in tasks
    ]

@app.post("/api/tasks")
async def create_task(task: TaskCreate, current_user: User = Depends(get_current_user)):  # Use User model
    task_dict = task.dict()
    task_dict["user_id"] = current_user.id  # Attribute access
    result = tasks_collection.insert_one(task_dict)
    return {"id": str(result.inserted_id), **task.dict()}

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str, current_user: User = Depends(get_current_user)):  # Use User model
    task = tasks_collection.find_one({"_id": ObjectId(task_id), "user_id": current_user.id})  # Attribute access
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"id": str(task["_id"]), "title": task["title"], "description": task["description"], "status": task["status"]}

@app.put("/api/tasks/{task_id}")
async def update_task(task_id: str, task: TaskUpdate, current_user: User = Depends(get_current_user)):  # Use User model
    result = tasks_collection.update_one(
        {"_id": ObjectId(task_id), "user_id": current_user.id},  # Attribute access
        {"$set": task.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task updated"}

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str, current_user: User = Depends(get_current_user)):  # Use User model
    result = tasks_collection.delete_one({"_id": ObjectId(task_id), "user_id": current_user.id})  # Attribute access
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}

# Web Interface Routes (unchanged)
@app.get("/")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/tasks")
async def tasks_page(request: Request):
    return templates.TemplateResponse("tasks.html", {"request": request})