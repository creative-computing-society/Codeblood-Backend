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
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Template
from os import getenv

from app.utils.jwt import verify_jwt

from app.registeration.models import RegisterTeam, JoinTeam, TeamDashboard, LeaveTeamRequest, RemoveFromTeamRequest

router = APIRouter()
logger = getLogger(__name__)

MAIL_USERNAME = getenv("MAIL_USERNAME")
print("MAIL_USERNAME:", MAIL_USERNAME)  # Debugging line to check if MAIL_USERNAME is set
MAIL_PASSWORD = getenv("MAIL_PASSWORD")
# assert MAIL_USERNAME and MAIL_PASSWORD, "MAIL_USERNAME and MAIL_PASSWORD must be set in environment variables"
MAIL_FROM = getenv("MAIL_FROM")
# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,  # App password
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,  
    MAIL_SSL_TLS=False, 
    USE_CREDENTIALS=True,
)


async def send_email(name: str, team_name: str, email: str, template_path: str):
    """
    Sends an email using the provided template and dynamic fields.
    """
    # Use absolute path for the template
    # absolute_template_path = "/app/app/registeration/TeamRegistration.html"

    with open(template_path, "r") as file:
        template = Template(file.read())
    html_content = template.render(name=name, team_name=team_name)

    message = MessageSchema(
        subject="Team Registration Confirmation",
        recipients=[email],
        body=html_content,
        subtype="html",
    )

    fm = FastMail(conf)
    await fm.send_message(message)

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

    email = payload.get("email")
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
    
@router.get("/verify")
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

    email = payload.get("email")
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

    team_name = data.team_name
    player_name = data.username
    discord_id = data.discord_id
    rollno = data.rollno

    check_user_task = teams.find_one({"players.email": user["email"]})
    check_team_task = teams.find_one({"team_name": team_name})
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

    team_info = generate_initial_team(team_name, player_name, user["email"], discord_id, rollno)
    team_info["players"][0]["rollno"] = rollno

    try:
        await teams.insert_one(team_info)
        await add_teamid_to_user(request, team_info.get("team_code", ""), user["email"])
        print(1)
        # Send email
        await send_email(
            name=player_name,
            team_name=team_name,
            email=user["email"],
            template_path="/app/app/registeration/TeamRegistration2.html",
        )
        print(2)
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
    discord_id = data.discord_id
    rollno = data.rollno

    existing = await teams.find_one({"team_code": team_code})

    if not existing:
        return JSONResponse(
            {"error": "Team code invalid or player already in team"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    for player in existing.get("players", []):
        if player["email"] == user["email"]:
            return JSONResponse(
                {"error": "Player already in team"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    update_info = add_player(team_code, data.username, user["email"], discord_id, rollno)
    result = await teams.update_one(*update_info)

    await add_teamid_to_user(request, team_code, user["email"])

    if result.modified_count == 0:
        return JSONResponse(
            {"error": "Maximum team capacity has been reached!"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Send email
    await send_email(
        name=data.username,
        team_name=existing["team_name"],
        email=user["email"],
        template_path="TeamRegistration.html",
    )

    return JSONResponse({"success": True})



@router.get("/team-dashboard")
@limiter.limit("15/minute") 
async def fetch_team_dashbaord(request: Request, user=Depends(get_current_user)):
    """
    Fetches the team dashboard for the logged-in user.
    Includes team details and the logged-in user's email.
    """
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

    # Add the current user's email to the response
    existing.update({"currentUserEmail": email})

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



@router.post("/leave-team")
@limiter.limit("10/minute")
async def leave_team(request: Request, data: LeaveTeamRequest, user=Depends(get_current_user)):
    """
    Allows a non-team leader user to leave a team.
    Updates the database to remove the user from the team.
    """
    teams: AsyncIOMotorCollection = request.app.state.teams

    email = data.email  # Extract email from JSON body

    # Find the team the user belongs to
    existing_team = await teams.find_one({"players.email": email})

    if not existing_team:
        return JSONResponse(
            {"error": "User is not part of any team"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Check if the user is the team leader
    if existing_team.get("team_leader_email") == email:
        return JSONResponse(
            {"error": "Team leader cannot leave the team. Use 'remove-from-team' instead."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Remove the user from the team
    try:
        await teams.update_one(
            {"team_code": existing_team["team_code"]},
            {"$pull": {"players": {"email": email}}}
        )
        return JSONResponse({"success": True}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error while removing user from team: {e}")
        return JSONResponse(
            {"error": "Failed to leave the team"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/remove-from-team")
@limiter.limit("10/minute")
async def remove_from_team(request: Request, data: RemoveFromTeamRequest, user=Depends(get_current_user)):
    """
    Allows the team leader to remove a user from the team.
    Updates the database to remove the specified user from the team.
    """
    teams: AsyncIOMotorCollection = request.app.state.teams

    email = user["email"]
    email_to_remove = data.email_to_remove  # Extract email_to_remove from JSON body

    # Find the team the leader belongs to
    existing_team = await teams.find_one({"players.email": email})

    if not existing_team:
        return JSONResponse(
            {"error": "Team leader is not part of any team"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Check if the user is the team leader
    if existing_team.get("team_leader_email") != email:
        return JSONResponse(
            {"error": "Only the team leader can remove members from the team"},
            status_code=status.HTTP_403_FORBIDDEN,
        )

    # Check if the user to remove exists in the team
    user_to_remove = next(
        (player for player in existing_team.get("players", []) if player["email"] == email_to_remove),
        None
    )
    if not user_to_remove:
        return JSONResponse(
            {"error": "User to remove is not part of the team"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Remove the user from the team
    try:
        await teams.update_one(
            {"team_code": existing_team["team_code"]},
            {"$pull": {"players": {"email": email_to_remove}}}
        )
        return JSONResponse({"success": True}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error while removing user from team: {e}")
        return JSONResponse(
            {"error": "Failed to remove the user from the team"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@router.delete("/delete-team")
@limiter.limit("5/minute")
async def delete_team(request: Request, user=Depends(get_current_user)):
    """
    Allows the team leader to delete the team if they are the only member.
    Updates the database to remove the team.
    """
    teams: AsyncIOMotorCollection = request.app.state.teams

    email = user["email"]

    
    existing_team = await teams.find_one({"team_leader_email": email})

    if not existing_team:
        return JSONResponse(
            {"error": "Team leader is not part of any team"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    
    if existing_team.get("team_leader_email") != email:
        return JSONResponse(
            {"error": "Only the team leader can delete the team"},
            status_code=status.HTTP_403_FORBIDDEN,
        )

    
    if len(existing_team.get("players", [])) > 1:
        return JSONResponse(
            {"error": "Team cannot be deleted as it has more than one member"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    
    try:
        await teams.delete_one({"team_code": existing_team["team_code"]})
        return JSONResponse({"success": True, "message": "Team deleted successfully"}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error while deleting team: {e}")
        return JSONResponse(
            {"error": "Failed to delete the team"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )