import os

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from pymongo import MongoClient
from bson import ObjectId
import secrets
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from typing import List

from main import app, authenticate_admin, db
from models.UserModel import UserCreate, UserResponse, UserUpdate


users_collection = db["users"]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@app.post("/admin/users/", response_model=UserResponse)
async def create_user(user: UserCreate, admin: str = Depends(authenticate_admin)):
    hashed_password = get_password_hash(user.password)
    user_data = user.dict()
    user_data["password"] = hashed_password
    result = users_collection.insert_one(user_data)
    return UserResponse(id=str(result.inserted_id), username=user.username, role=user.role)

@app.get("/admin/users/", response_model=List[UserResponse])
async def list_users(admin: str = Depends(authenticate_admin)):
    users = []
    for user_data in users_collection.find():
        users.append(
            UserResponse(id=str(user_data.pop("_id")), username=user_data["username"], role=user_data["role"]))
    return users

@app.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserUpdate, admin: str = Depends(authenticate_admin)):
    try:
        object_id = ObjectId(user_id)
        user_data = {k: v for k, v in user.dict(exclude_unset=True).items()}
        if "password" in user_data:
            user_data["password"] = get_password_hash(user_data["password"])
        result = users_collection.update_one({"_id": object_id}, {"$set": user_data})
        if result.modified_count > 0:
            user_updated = users_collection.find_one({"_id": object_id})
            return UserResponse(id=str(user_updated.pop("_id")), username=user_updated["username"],
                                role=user_updated["role"])
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.delete("/admin/users/{user_id}", response_model=dict)
async def delete_user(user_id: str, admin: str = Depends(authenticate_admin)):
    result = users_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count > 0:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")