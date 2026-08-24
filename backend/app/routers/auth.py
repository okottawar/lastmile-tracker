from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.auth import UserRegister, Token
router=APIRouter(prefix="/api/auth",tags=["auth"])
@router.post("/register",response_model=Token,status_code=201)
async def register(payload:UserRegister,db:AsyncSession=Depends(get_db)):
    if payload.role!=UserRole.CUSTOMER: raise HTTPException(status_code=403,detail="Public registration is only allowed for customer accounts.")
    if (await db.execute(select(User).where(User.email==payload.email))).scalar_one_or_none(): raise HTTPException(status_code=409,detail="Email already registered.")
    user=User(name=payload.name,email=payload.email,phone=payload.phone,hashed_password=hash_password(payload.password),role=UserRole.CUSTOMER); db.add(user); await db.commit(); await db.refresh(user)
    return Token(access_token=create_access_token({"sub":str(user.id),"role":user.role.value}),role=user.role,user_id=user.id,name=user.name)
@router.post("/login",response_model=Token)
async def login(form_data:OAuth2PasswordRequestForm=Depends(),db:AsyncSession=Depends(get_db)):
    user=(await db.execute(select(User).where(User.email==form_data.username))).scalar_one_or_none()
    if not user or not verify_password(form_data.password,user.hashed_password): raise HTTPException(status_code=401,detail="Incorrect email or password",headers={"WWW-Authenticate":"Bearer"})
    return Token(access_token=create_access_token({"sub":str(user.id),"role":user.role.value}),role=user.role,user_id=user.id,name=user.name)
