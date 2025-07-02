import uvicorn
from fastapi import FastAPI
import socketio

from .config import IS_DEV
from app.auth.middleware import SessionMiddleware
from app.socketio.handlers import register_handlers as app_register_handlers
from app.auth.routes import router as app_auth_router

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
fastapi_app = FastAPI()

@fastapi_app.get("/test")
async def test_backend():
    return {"message": "YAY...CHALRA HAI BHAI LOG"}

fastapi_app.include_router(app_auth_router)

fastapi_app.add_middleware(SessionMiddleware)

fastapi_app.state.sio = sio 

app_register_handlers(sio)

app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.1.0", port=3021, reload=IS_DEV)
