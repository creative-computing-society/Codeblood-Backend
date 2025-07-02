import uvicorn
from fastapi import FastAPI
from socketio import AsyncServer, ASGIApp

from config import IS_DEV, phase, PHASE_TO_BUNDLES
from app import bundle as appBundle
from phase1 import bundle as phase1Bundle

Bundles = {
    "App": appBundle,
    "Phase 1": phase1Bundle
}

sio = AsyncServer(async_mode="asgi", cors_allowed_origins="*")
fastapi_app = FastAPI()

@fastapi_app.get("/test")
async def test_backend():
    return {"message": "YAY...CHALRA HAI BHAI LOG"}

def load_bundle(package_data):
    print()
    if "router" in package_data:
        fastapi_app.include_router(package_data["router"])
    if "middleware" in package_data:
        fastapi_app.add_middleware(package_data["middleware"])
    if "socket_handler" in package_data:
        package_data["socket_handler"](sio)

if __name__ == "__main__":
    fastapi_app.state.sio = sio

    print("Phase:", phase, end='')
    bundles = PHASE_TO_BUNDLES[phase]
    for bundle in bundles:
        load_bundle(Bundles[bundle])
        print("Loaded bundle:", bundle, end='')
    print()

    app = ASGIApp(sio, other_asgi_app=fastapi_app)
    uvicorn.run("main:app", host="127.0.1.0", port=3021, reload=IS_DEV)
