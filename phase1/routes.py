from logging import getLogger
from fastapi import APIRouter, Request
from config import get_is_mocks
from mock_data import mockActivity
from .db_interface import get_logs

router = APIRouter()
logger = getLogger(__name__)


@router.get("/get-activity-logs")
async def login(request: Request):
    if request.state.user_id is None:
        return []
    logger.debug("HTTP - Get Activity Logs")
    if get_is_mocks():
        return mockActivity
    return get_logs()