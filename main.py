from loggers.loggers import setup_logging

import asyncio
from contextlib import asynccontextmanager
import uvicorn
import argparse
from dotenv import load_dotenv
from os import getenv
from fastapi import FastAPI
from socketio import AsyncServer, ASGIApp
from logging import getLogger
from threader import clean_up

setup_logging()

# IMPORTS ARE IN THIS ORDER FOR A REASON
# DO NOT CHANGE THE ORDER OF THE IMPORTS OR YOU WILL MEET THE CODING GODS
from config import PHASE_TO_BUNDLES, set_config
from db import init_db

init_db()

from app import bundle as appBundle
from phase1 import bundle as phase1Bundle

load_dotenv()

Bundles = {"App": appBundle, "Phase 1": phase1Bundle}

MINUTE = 60

logger = getLogger(__name__)


async def threads_cleanup():
    while True:
        clean_up_num = clean_up()
        if clean_up_num != 0:
            logger.info(f"Cleaned up {clean_up_num} async database operatons")
        await asyncio.sleep(1 * MINUTE)


@asynccontextmanager
async def boot(_app):
    asyncio.create_task(threads_cleanup())
    yield


sio = AsyncServer(async_mode="asgi", cors_allowed_origins="*")
fastapi_app = FastAPI(lifespan=boot)


@fastapi_app.get("/test")
async def test_backend():
    return {"message": "YAY...CHALRA HAI BHAI LOG"}


def set_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--phase",
        help="Choose the phase of the application (Default: Phase 1)",
        default="Phase 1",
    )
    parser.add_argument(
        "-d", "--dev", help="Run code in dev mode? (Default: true)", default="true"
    )
    args = parser.parse_args()
    args.dev = str(args.dev).lower() == "true"  # Convert to bool

    set_config(args.dev, args.phase)

    return args


def load_bundle(package_data):
    if "router" in package_data:
        fastapi_app.include_router(package_data["router"])
    if "middleware" in package_data:
        fastapi_app.add_middleware(
            package_data["middleware"], secret_key=getenv("SECRET_KEY")
        )
    if "socket_handler" in package_data:
        package_data["socket_handler"](sio)


fastapi_app.state.sio = sio

args = set_args()

logger.info(f"Phase: {args.phase}")
bundles = PHASE_TO_BUNDLES[args.phase]

for bundle in bundles:
    try:
        load_bundle(Bundles[bundle])
        logger.info(f"Loaded bundle: {bundle}")
    except:
        logger.info(f"Failed to load bundle: {bundle}")

app = ASGIApp(sio, other_asgi_app=fastapi_app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=3021, reload=args.dev)
