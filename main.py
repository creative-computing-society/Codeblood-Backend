import uvicorn
import argparse
from fastapi import FastAPI
from socketio import AsyncServer, ASGIApp
from logging import getLogger


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--phase", help="Choose the phase of the application (Default: Phase 0)", default="Phase 0")
parser.add_argument("-d", "--dev", help="Run code in dev mode? (Default: true)", default="true")
args = parser.parse_args()
args.dev = str(args.dev).lower() == "true" # Convert to bool

from config import PHASE_TO_BUNDLES, set_config
set_config(args.dev, args.phase)

from app import bundle as appBundle
from phase1 import bundle as phase1Bundle

Bundles = {
    "App": appBundle,
    "Phase 1": phase1Bundle
}

sio = AsyncServer(async_mode="asgi", cors_allowed_origins="*")
fastapi_app = FastAPI()

logger = getLogger(__name__)


@fastapi_app.get("/test")
async def test_backend():
    return {"message": "YAY...CHALRA HAI BHAI LOG"}


def load_bundle(package_data):
    if "router" in package_data:
        fastapi_app.include_router(package_data["router"])
    if "middleware" in package_data:
        fastapi_app.add_middleware(package_data["middleware"])
    if "socket_handler" in package_data:
        package_data["socket_handler"](sio)


if __name__ == "__main__":
    fastapi_app.state.sio = sio

    logger.info(f"Phase: {args.phase}")
    bundles = PHASE_TO_BUNDLES[args.phase]
    for bundle in bundles:
        try:
            load_bundle(Bundles[bundle])
            logger.info(f"Loaded bundle: {bundle}")
        except:
            logger.error(f"Failed to load bundle: {bundle}")

    app = ASGIApp(sio, other_asgi_app=fastapi_app)
    uvicorn.run("main:app", host="127.0.1.0", port=3021, reload=args.dev)
