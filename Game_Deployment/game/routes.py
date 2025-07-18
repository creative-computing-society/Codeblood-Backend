from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from app.utils.jwt import verify_jwt
from app.database import teams, points, players, lobbies
from app.game.models import Lobby, Points, Player
from uuid import uuid4
from datetime import datetime
import json
from app.limitting import limiter

game_router = APIRouter()

@game_router.post("/set_lobby")
@limiter.limit("10/minute")
async def set_lobby(request: Request):
    token = request.cookies.get("session_token")
    if not token:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    payload = verify_jwt(token)
    email = payload.get("email")
    if not email:
        return JSONResponse({"error": "Invalid session token"}, status_code=400)

    # Check if the player exists in the teams collection
    team = await teams.find_one({"players.email": email})
    if not team:
        return JSONResponse({"error": "Player Not Registered"}, status_code=404)

    team_code = team["team_code"]

    # Check if the team exists in the lobbies collection
    lobby = await lobbies.find_one({"team_code": team_code})
    if not lobby:
        lobby_id = str(uuid4())[:8]
        lobby_data = {
            "lobby_id": lobby_id,
            "team_code": team_code,
            "players": team["players"]
        }
        await lobbies.insert_one(lobby_data)
        lobby = Lobby(**lobby_data)  # Validate and structure using Pydantic
    else:
        lobby = Lobby(**lobby)  # Validate existing lobby data

    return JSONResponse(lobby.dict())

@game_router.post("/check_answer")
@limiter.limit("15/minute")
async def check_answer(question_id: str, answer: str, team_id: str):
    # Load the local JSON file with questions and answers
    with open("questions.json", "r") as f:
        questions = json.load(f)

    question = questions.get(question_id)
    if not question:
        return JSONResponse({"error": "Invalid question ID"}, status_code=400)

    if question["Answer"] == answer:
        await points.update_one(
            {"team_code": team_id},
            {"$inc": {"Points": question["Points"], "Question_solved": 1}}
        )
        return JSONResponse({"message": "Correct answer!"})
    else:
        return JSONResponse({"message": "Wrong answer!"})

@game_router.post("/team_status_update")
@limiter.limit("10/minute") 
async def team_status_update(level_number: int, action: str, team_id: str):
    now = datetime.utcnow()
    if action == "entered":
        await points.update_one(
            {"team_code": team_id},
            {"$set": {"Current_level": level_number, "Current_Level_Entered_At": now}}
        )
    elif action == "exited":
        team = await points.find_one({"team_code": team_id})
        if not team or not team.get("Current_Level_Entered_At"):
            return JSONResponse({"error": "Invalid team data"}, status_code=400)
        time_spent = (now - team["Current_Level_Entered_At"]).total_seconds()
        await points.update_one(
            {"team_code": team_id},
            {"$inc": {"Levels_Cleared": 1, "Total_Time_To_Clear_Levels": time_spent}}
        )
    return JSONResponse({"message": "Team status updated"})

@game_router.post("/individual_status_update")
@limiter.limit("10/minute")
async def individual_status_update(username: str, level: int, checkpoint: int):
    await players.update_one(
        {"user_name": username},
        {"$set": {f"Status.{level}": checkpoint}}
    )
    return JSONResponse({"message": "Player status updated"})

@game_router.get("/leaderboard")
@limiter.limit("5/minute")
async def leaderboard():
    teams_data = await points.find().to_list(None)
    leaderboard = sorted(
        [Points(**team) for team in teams_data],  # Validate and structure using Pydantic
        key=lambda x: (-x.Points, x.Total_Time_To_Clear_Levels, -x.Levels_Cleared)
    )
    return JSONResponse([team.dict() for team in leaderboard])