from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from app.utils.jwt import verify_jwt
from app.database import teams, points, players, lobbies
from app.game.models import Lobby, Points, Player
from uuid import uuid4
from datetime import datetime
import json
from app.limitting import limiter
from app.utils.auth import verify_cookie

game_router = APIRouter()

with open("questions.json", "r") as f:
    QUESTIONS = json.load(f)

@game_router.post("/set_lobby")
@limiter.limit("10/minute")
async def set_lobby(request: Request, email: str = Depends(verify_cookie)):
    team = await teams.find_one({"players.email": email})
    if not team:
        return JSONResponse({"error": "Player Not Registered"}, status_code=404)

    player_data = next(
        (player for player in team["players"] if player["email"] == email), None
    )
    if not player_data:
        return JSONResponse({"error": "Player not found in the team"}, status_code=404)

    player_data["is_hacker"] = player_data.get("is_hacker", False)
    player_data["is_wizard"] = player_data.get("is_wizard", False)

    team_code = team["team_code"]
    lobby = await lobbies.find_one({"team_code": team_code})
    if not lobby:
        lobby_id = str(uuid4())[:8]
        lobby_data = {
            "lobby_id": lobby_id,
            "team_code": team_code,
            "players": team["players"],  
        }
        await lobbies.insert_one(lobby_data)
        lobby = lobby_data

    response_data = {
        "lobby_id": lobby["lobby_id"],
        "team_code": team_code,
        "player": player_data,  # Only the logged-in user's data
    }

    return JSONResponse(response_data)


@game_router.post("/check_answer")
@limiter.limit("15/minute")
async def check_answer(request: Request, question_id: str, answer: str, team_id: str, email: str = Depends(verify_cookie)):
    question = QUESTIONS.get(question_id)
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
async def team_status_update(request: Request, level_number: int, action: str, team_id: str, email: str = Depends(verify_cookie)):
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
async def individual_status_update(request: Request, username: str, level: int, checkpoint: int, email: str = Depends(verify_cookie)):
    await players.update_one(
        {"user_name": username},
        {"$set": {f"Status.{level}": checkpoint}}
    )
    return JSONResponse({"message": "Player status updated"})

@game_router.get("/leaderboard")
@limiter.limit("5/minute")
async def leaderboard(request: Request, email: str = Depends(verify_cookie)):
    teams_data = await points.find().to_list(None)
    leaderboard = sorted(
        [Points(**team) for team in teams_data],
        key=lambda x: (-x.Points, x.Total_Time_To_Clear_Levels, -x.Levels_Cleared)
    )
    return JSONResponse([team.dict() for team in leaderboard])