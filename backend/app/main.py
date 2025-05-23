from fastapi import FastAPI
from app.routes.health_check import health_router
from app.routes.chat_routes import chat_router

app = FastAPI()

app.include_router(health_router)
app.include_router(chat_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=1, reload=True)
