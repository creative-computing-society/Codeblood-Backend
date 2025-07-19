from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from app.utils.jwt import verify_jwt
from app.database import teams, points, players, lobbies
from app.game.models import Lobby, Points, Player, TeamStatusUpdatePayload, IndividualStatusUpdatePayload, CheckAnswerPayload
from uuid import uuid4
from datetime import datetime
import json
from app.limitting import limiter
from app.utils.auth import verify_cookie
import os
game_router = APIRouter()
from pathlib import Path


current_dir = Path(__file__).parent


questions_path = current_dir / "questions.json"


with open(questions_path, "r") as f:
    QUESTIONS = json.load(f)

@game_router.post("/set_lobby")
@limiter.limit("10/minute")
async def set_lobby(request: Request, email: str = Depends(verify_cookie)):

    lobbies = request.app.state.lobbies
    teams = request.app.state.teams

    if not lobbies or not teams:
        return JSONResponse({"error": "Database collections not initialized"}, status_code=500)

    team = await teams.find_one({"players.email": email}, {"players.$": 1, "team_code": 1})
    if not team:
        return JSONResponse({"error": "Player not registered in any team"}, status_code=404)

    player_data = team["players"][0]
    player = Player(**player_data)  

    
    team_code = team["team_code"]
    lobby = await lobbies.find_one({"team_code": team_code})
    if not lobby:
        
        lobby_id = str(uuid4())[:8]
        lobby_data = Lobby(
            lobby_id=lobby_id,
            team_code=team_code,
            players=[Player(**p) for p in team["players"]]
        )
        await lobbies.insert_one(lobby_data.dict())
        lobby = lobby_data.dict()

    
    response_data = {
        "lobby_id": lobby["lobby_id"],
        "team_code": team_code,
        "player": player.dict(),  # Only the logged-in user's data
    }

    return JSONResponse(response_data)


@game_router.post("/check_answer")
@limiter.limit("15/minute")
async def check_answer(request : Request , payload: CheckAnswerPayload, email: str = Depends(verify_cookie)):
    question = QUESTIONS.get(payload.question_id)
    if not question:
        return JSONResponse({"error": "Invalid question ID"}, status_code=400)

    if question["Answer"] == payload.answer:
        result = await points.update_one(
            {"team_code": payload.team_id},
            {"$inc": {"Points": question["Points"], "Question_solved": 1}},
        )
        if result.matched_count == 0:
            return JSONResponse({"error": "Team not found"}, status_code=404)

        return JSONResponse({"message": "Correct answer!"})
    else:
        return JSONResponse({"message": "Wrong answer!"})

@game_router.post("/team_status_update")
@limiter.limit("10/minute")
async def team_status_update(request : Request, payload: TeamStatusUpdatePayload, email: str = Depends(verify_cookie)):
    now = datetime.utcnow()

    team_data = await points.find_one({"team_code": payload.team_id})
    if not team_data:
        return JSONResponse({"error": "Invalid team ID"}, status_code=400)

    try:
        team = Points(**team_data)  
    except Exception as e:
        return JSONResponse({"error": f"Data validation error: {str(e)}"}, status_code=500)

    if team.Current_Level_Entered_At:
        time_spent = (now - team.Current_Level_Entered_At).total_seconds()
        update_data = {
            "$inc": {"Levels_Cleared": 1, "Total_Time_To_Clear_Levels": time_spent},
            "$set": {"Current_level": payload.level_number, "Current_Level_Entered_At": now},
        }
    else:
        update_data = {
            "$set": {"Current_level": payload.level_number, "Current_Level_Entered_At": now},
        }

    result = await points.update_one({"team_code": payload.team_id}, update_data)
    if result.matched_count == 0:
        return JSONResponse({"error": "Failed to update team status"}, status_code=500)

    return JSONResponse({"message": "Team status updated"})


@game_router.post("/individual_status_update")
@limiter.limit("10/minute")
async def individual_status_update(request : Request, payload: IndividualStatusUpdatePayload, email: str = Depends(verify_cookie)):
    result = await players.update_one(
        {"user_name": payload.username},
        {"$set": {f"Status.{payload.level}": payload.checkpoint}},
    )

    if result.matched_count == 0:
        return JSONResponse({"error": "Player not found"}, status_code=404)

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