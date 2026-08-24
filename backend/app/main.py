from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.core.database import init_db
from app.routers import auth,admin,orders
settings=get_settings()
@asynccontextmanager
async def lifespan(app:FastAPI):
    await init_db();yield
app=FastAPI(title=settings.APP_NAME,description="Last-Mile Delivery Tracker API",version="1.0.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.CORS_ORIGINS.split(",") if x.strip()],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(auth.router);app.include_router(admin.router);app.include_router(orders.router)
@app.get("/")
async def root(): return {"status":"ok","service":settings.APP_NAME}
@app.get("/api/health")
async def health(): return {"status":"healthy"}
