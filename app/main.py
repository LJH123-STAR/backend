from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import dashboard, compose, projects, review
from app.database import engine
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI双语法理编曲系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8080",
        "https://frontend-lovat-nu-26.vercel.app"    # 添加你的前端域名
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(compose.router)
app.include_router(projects.router)
app.include_router(review.router)

@app.get("/")
def root():
    return {"message": "AI双语法理编曲系统API"}
