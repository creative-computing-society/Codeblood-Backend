from logging import getLogger
from fastapi import APIRouter, Request
from starlette.responses import JSONResponse

from config import get_is_mocks
from mock_data import mockActivity
from .db_interface import get_logs

router = APIRouter()
logger = getLogger(__name__)


@router.get("/get-activity-logs")
async def login(_request: Request):
    logger.debug("HTTP - Get Activity Logs")
    if get_is_mocks():
        return mockActivity
    return get_logs()

@router.get("/get-self-team")
async def self_team(request: Request):
    logger.debug("HTTP - Self Team")
    return JSONResponse({
        "team_name": request.state.session["team_name"],
        "team_id": request.state.session["team_id"]
    })
