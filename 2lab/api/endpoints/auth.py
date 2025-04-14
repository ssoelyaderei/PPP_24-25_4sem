from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Добавьте этот импорт
from app.core.security import get_current_user, create_access_token, verify_password
from app.crud.user import get_user_by_email, create_user
from app.db.session import get_db
from app.schemas.user import UserCreate, UserOut, Token

router = APIRouter()

@router.post("/sign-up/", response_model=UserOut)
def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)

@router.post("/login/", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/", response_model=UserOut)
def read_users_me(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)  # Теперь get_current_user доступен
):
    user = get_user_by_email(db, email=current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user