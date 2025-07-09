from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from logging import getLogger
from motor.motor_asyncio import AsyncIOMotorCollection

from oauth import get_current_user
from utils import generate_initial_team, add_player

from .models import RegisterTeam, JoinTeam

router = APIRouter()
logger = getLogger(__name__)


@router.post("/create-team")
async def register_team(
    request: Request, data: RegisterTeam, user=Depends(get_current_user)
):
    teams: AsyncIOMotorCollection = request.app.state.teams

    team_name = data.team_name
    player_name = data.username

    existing = await teams.find_one({"team_name": team_name})

    # NOTE: We do not validate user as we are getting that data from OAuth
    if existing:
        return JSONResponse(
            {"error": "Team already exists"}, status_code=status.HTTP_400_BAD_REQUEST
        )

    if data.is_wizard and data.is_hacker:
        return JSONResponse(
            {
                "error": "User is trying to be both hacker and wizzard, so let them"
            },  # Ofcourse we wont allow this but its funny to display this
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    team_info = generate_initial_team(
        team_name, player_name, user["email"], data.is_hacker, data.is_wizard
    )

    try:
        await teams.insert_one(team_info)

        return JSONResponse({"team_code": team_info.get("team_code")})

    except Exception as e:
        logger.critical(f"CRITICAL ERROR: {e}")
        await teams.delete_one({"team_code": team_info.get("team_code")})


@router.post("/join-team")
async def join_team(request: Request, data: JoinTeam, user=Depends(get_current_user)):
    teams: AsyncIOMotorCollection = request.app.state.teams

    team_code = data.team_code

    existing = await teams.find_one(
        {"team_code": team_code, "players.email": user["email"]}
    )

    if not existing:
        return JSONResponse(
            {"error": "Team code invalid or player already in team"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if data.is_wizard and data.is_hacker:
        return JSONResponse(
            {
                "error": "User is trying to be both hacker and wizzard, so let them"
            },  # Ofcourse we wont allow this but its funny to display this
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    update_info = add_player(
        team_code, data.username, user["email"], data.is_hacker, data.is_wizard
    )
    result = await teams.update_one(*update_info)

    if result.modified_count == 0:
        return JSONResponse(
            {"error": "Maximum team capacity has been reached!"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return JSONResponse({"success": True})
