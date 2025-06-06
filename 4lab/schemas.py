from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class UserBase(BaseModel):
    name: str = Field(..., min_length=1)

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

class PostBase(BaseModel):
    text: str = Field(..., min_length=1)
    user_id: int

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    text: str = Field(..., min_length=1)

class Post(PostBase):
    id: int
    date_of_creation: datetime
    class Config:
        orm_mode = True

class UserWithPosts(User):
    posts: List[Post] = []