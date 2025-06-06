from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .. import schemas, models
from ..database import SessionLocal

router = APIRouter(prefix="/posts", tags=["posts"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.Post])
def read_posts(user_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    query = db.query(models.Post)
    if user_id is not None:
        query = query.filter(models.Post.user_id == user_id)
    return query.all()

@router.post("/", response_model=schemas.Post, status_code=status.HTTP_201_CREATED)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == post.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db_post = models.Post(text=post.text, owner=user)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@router.put("/{post_id}", response_model=schemas.Post)
def update_post(post_id: int, post_update: schemas.PostUpdate, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.text = post_update.text
    db.commit()
    db.refresh(post)
    return post