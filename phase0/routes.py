from logging import getLogger
from fastapi import APIRouter, Request
from .db_interface import assign_team_to_user, create_team_registration

router = APIRouter()
logger = getLogger(__name__)

@router.post("/register")
async def register_team(request: Request):
    data = await request.json()
    team_name = data["team_name"]
    join_code = create_team_registration(team_name, request.state.session["user_id"])
    return {"code": join_code}


@router.get("/join-team")
async def join_team(request: Request):
    logger.debug("HTTP - Join Team")
    data = await request.json()
    join_code = data["code"]
    assign_team_to_user(request.state.session["user_id"], join_code)
    return {"status": "ok"}