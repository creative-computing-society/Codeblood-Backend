import asyncio
from typing import Any, Dict, Optional, cast
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from logging import getLogger
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError
from slowapi import Limiter
from app.oauth import get_current_user
from app.utils import generate_initial_team, add_player, add_teamid_to_user
from app.limitting import limiter

from app.utils.jwt import verify_jwt

from app.registeration.models import RegisterTeam, JoinTeam, TeamDashboard

router = APIRouter()
logger = getLogger(__name__)



@router.get("/checkRegistered")
@limiter.limit("20/minute") 
async def is_authenticated(request: Request):
    """
    Checks if the user has a valid session cookie and exists in the DB.
    """
    token = request.cookies.get("session_token")
    if not token:
        return {"registered": False}

    payload = verify_jwt(token)
    if not payload:
        return {"registered": False}

    email = payload.get("sub")
    if not email:
        return {"registered": False}

    users = request.app.state.users
    user = await users.find_one({"email": email})

    if not user:
        return {"registered": False}
    
    teams: AsyncIOMotorCollection = request.app.state.teams

    existing_team = await teams.find_one({"players.email": email})

    if existing_team:
        return {"registered": True}
    else:
        return {"registered": False}
    
@router.get("/verufy")
@limiter.limit("20/minute")
async def token_verify(request: Request):
    """
    Verifies the validity of the session token received in the cookie.
    Returns a boolean indicating whether the token is valid or not.
    """
    token = request.cookies.get("session_token")
    if not token:
        return {"valid": False}

    payload = verify_jwt(token)
    if not payload:
        return {"valid": False}

    email = payload.get("sub")
    if not email:
        return {"valid": False}

    users = request.app.state.users
    user = await users.find_one({"email": email})

    if not user:
        return {"valid": False}

    return {"valid": True}

@router.post("/create-team")
@limiter.limit("10/minute") 
async def register_team(
    request: Request, data: RegisterTeam, user=Depends(get_current_user)
):
    teams: AsyncIOMotorCollection = request.app.state.teams
    users: AsyncIOMotorCollection = request.app.state.users

    team_name = data.team_name
    player_name = data.username
    discord_id = data.discord_id  # Extract discord_id

    # Check to see if user is in any other team
    check_user_task = teams.find_one({"players.email": user["email"]})

    # Check to see if team name is taken or not
    check_team_task = teams.find_one({"team_name": team_name})

    # Runs them parrallely cause why not
    user_in_team, team_exists = await asyncio.gather(check_user_task, check_team_task)

    if user_in_team:
        return JSONResponse(
            {"error": "User has already joined a team!"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if team_exists:
        return JSONResponse(
            {"error": "Team already exists"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    team_info = generate_initial_team(team_name, player_name, user["email"], discord_id)

    try:
        await teams.insert_one(team_info)

        # Add _id of team to user as "team_id" tag
        await add_teamid_to_user(request, team_info.get("team_code", ""), user["email"])

        return JSONResponse({"team_code": team_info.get("team_code")})

    except DuplicateKeyError:
        return JSONResponse(
            {"error": "Team name already exists"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        logger.critical(f"CRITICAL ERROR: {e}")
        await teams.delete_one({"team_code": team_info.get("team_code")})
        return JSONResponse(
            {"error": "Internal Server Error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@router.post("/join-team")
@limiter.limit("10/minute") 
async def join_team(request: Request, data: JoinTeam, user=Depends(get_current_user)):
    teams: AsyncIOMotorCollection = request.app.state.teams

    team_code = data.team_code
    discord_id = data.discord_id  # Extract discord_id

    existing = await teams.find_one({"team_code": team_code})

    if not existing:
        return JSONResponse(
            {"error": "Team code invalid or player already in team"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Check if player is already part of the team
    for player in existing.get("players", []):
        if player["email"] == user["email"]:
            return JSONResponse(
                {"error": "Player already in team"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    update_info = add_player(team_code, data.username, user["email"], discord_id)
    result = await teams.update_one(*update_info)

    # Add _id of team to user as "team_id" tag
    await add_teamid_to_user(request, team_code, user["email"])

    if result.modified_count == 0:
        return JSONResponse(
            {"error": "Maximum team capacity has been reached!"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return JSONResponse({"success": True})




@router.get("/team-dashboard")
@limiter.limit("15/minute") 
async def fetch_team_dashbaord(request: Request, user=Depends(get_current_user)):
    teams: AsyncIOMotorCollection = request.app.state.teams

    email = user["email"]

    existing: Optional[Dict[str, Any]] = await teams.find_one({"players.email": email})

    if not existing:
        return JSONResponse(
            {"error": "Player not part of team"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Forcing query to be of Dict[str, Any] cause PyRight got confused
    existing = cast(Dict[str, Any], existing)

    # We are assuming that the initial check in "/create-team" and "/join-team" will prevent the user being in 2 teams
    is_leader: bool = existing.get("team_leader_email") == email

    # Remove _id tag cause whats frontend gonna do with it?
    existing.pop("_id")
    existing.update({"is_leader": is_leader})

    # Check if `is_wizard` and `is_hacker` exist in the database
    for player in existing.get("players", []):
        if player["email"] == email:
            if "is_wizard" in player:
                existing.update({"is_wizard": player["is_wizard"]})
            if "is_hacker" in player:
                existing.update({"is_hacker": player["is_hacker"]})
            break

    return JSONResponse(existing)



@router.post("/team-dashboard")
@limiter.limit("15/minute") 
async def update_team_dashboard(
    request: Request, data: TeamDashboard, user=Depends(get_current_user)
):
    teams: AsyncIOMotorCollection = request.app.state.teams

    team_code = data.team_code
    players = data.players

    existing = await teams.find_one({"team_code": team_code})

    if not existing:
        return JSONResponse(
            {"error": "Frontend, why are you giving me a bad request"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    hacker_count, wizard_count = 0, 0

    for player in players:
        if player.is_hacker:
            hacker_count += 1
        elif player.is_wizard:
            wizard_count += 1
        else:
            return JSONResponse(
                {"error": "Invalid wizard/hacker count"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    if hacker_count > 2 or wizard_count > 2:
        return Response(
            "User is trying to have more than 2 wizard/hacker, now you have 4 wizards",
            status_code=status.HTTP_400_BAD_REQUEST,
        )  # I love messing with users

    # Convert Player objects to dictionaries
    players_dict = [player.dict() for player in players]

    try:
        await teams.update_one({"team_code": team_code}, {"$set": {"players": players_dict}})
    except Exception as e:
        logger.error(f"HOUSTON, WE HAVE A PROBLEM: {e}")
        await teams.update_one(
            {"team_code": team_code}, {"$set": {"players": existing["players"]}}
        )
        return JSONResponse(
            {"error": "Database update failed, reverted to previous state"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return JSONResponse({"success": True}, status_code=status.HTTP_200_OK)
