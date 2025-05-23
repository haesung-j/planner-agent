from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.health_check import health_router
from app.routes.chat_routes import chat_router
import os

app = FastAPI()


allowed_origins = [
    "http://frontend:8501",  # Streamlit 프론트엔드 (컨테이너 간 통신)
    "http://localhost:8501",  # 로컬 개발용
    "http://127.0.0.1:8501",  # 로컬 개발용
    "http://nginx",  # nginx 프록시
    "http://localhost",  # nginx를 통한 외부 접근
    "http://127.0.0.1",  # nginx를 통한 외부 접근
    "http://localhost:3000",  # 개발 시 직접 프론트엔드 접근
]

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(chat_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=1, reload=True)
