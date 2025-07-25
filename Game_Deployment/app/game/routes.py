from fastapi import APIRouter, Request, Depends, Query
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
from bson.json_util import dumps
game_router = APIRouter()
from pathlib import Path


current_dir = Path(__file__).parent


questions_path = current_dir / "questions.json"


with open(questions_path, "r") as f:
    QUESTIONS = json.load(f)

@game_router.post("/set_lobby")
@limiter.limit("10/minute")
async def set_lobby(request: Request, email: str = Depends(verify_cookie)):
    
    # Access the lobbies and teams collections
    lobbies = request.app.state.lobbies
    teams = request.app.state.teams

    if lobbies is None or teams is None:
        return JSONResponse({"error": "Database collections not initialized"}, status_code=500)

    # Fetch the user's team and player data in a single query
    team = await teams.find_one({"players.email": email}, {"players.$": 1, "team_code": 1})
    if team is None:
        return JSONResponse({"error": "Player not registered in any team"}, status_code=404)

    # Extract the logged-in player's data
    player_data = team["players"][0]

    # Check if a lobby already exists for the team
    team_code = team["team_code"]
    lobby = await lobbies.find_one({"team_code": team_code})
    if lobby is None:
        # Create a new lobby if it doesn't exist
        lobby_id = str(uuid4())[:8]
        lobby_data = {
            "lobby_id": lobby_id,
            "team_code": team_code,
            "players": team["players"],  # Use raw player data without Pydantic validation
        }
        await lobbies.insert_one(lobby_data)
        lobby = lobby_data

    # Prepare the response
    response_data = {
        "lobby_id": lobby["lobby_id"],
        "team_code": team_code,
        "player": player_data,  # Only the logged-in user's data
    }

    return JSONResponse(response_data)

@game_router.post("/check_answer")
@limiter.limit("15/minute")
async def check_answer(request : Request, payload: CheckAnswerPayload, email: str = Depends(verify_cookie)):
    points = request.app.state.points  # Access the points collection from app state
    if points is None:
        return JSONResponse({"error": "Points collection not initialized"}, status_code=500)

    question = QUESTIONS.get(payload.question_id)
    if not question:
        return JSONResponse({"error": "Invalid question ID"}, status_code=400)

    if question["Answer"].lower() == payload.answer.lower():
        result = await points.update_one(
            {"team_code": payload.team_id},
            {"$inc": {"Points": question["Points"], "Question_solved": 1}},
            upsert=True
        )

        return JSONResponse({"message": "Correct answer!"})
    else:
        return JSONResponse({"message": "Wrong answer!"})

@game_router.post("/team_status_update")
@limiter.limit("10/minute")
async def team_status_update(request: Request, payload: TeamStatusUpdatePayload, email: str = Depends(verify_cookie)):
    now = datetime.utcnow()
    points = request.app.state.points  # Access the points collection from app state

    if points is None:
        return JSONResponse({"error": "Points collection not initialized"}, status_code=500)

    # Fetch the team data
    team_data = await points.find_one({"team_code": payload.team_id})
    if not team_data:
        return JSONResponse({"error": "Invalid team ID"}, status_code=400)

    # Check if the team has a previous level entry time
    if team_data.get("Current_Level_Entered_At"):
        time_spent = (now - team_data["Current_Level_Entered_At"]).total_seconds()
        update_data = {
            "$inc": {"Levels_Cleared": 1, "Total_Time_To_Clear_Levels": time_spent},
            "$set": {"Current_level": payload.level_number, "Current_Level_Entered_At": now},
        }
    else:
        # If no previous level entry time, just set the current level and entry time
        update_data = {
            "$set": {"Current_level": payload.level_number, "Current_Level_Entered_At": now},
        }

    # Perform the update
    result = await points.update_one({"team_code": payload.team_id}, update_data, upsert=True)
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
async def leaderboard(request: Request, skip: int = Query(0), limit: int = Query(10)):
    points = request.app.state.points  # Access the points collection from app state
    if points is None:
        return JSONResponse({"error": "Points collection not initialized"}, status_code=500)

    try:
        # Fetch and sort leaderboard data by Points only, with pagination
        teams_data_cursor = points.find().sort("Points", -1).skip(skip).limit(limit)
        teams_data = await teams_data_cursor.to_list(None)

        # Use bson.json_util.dumps to serialize ObjectId and other BSON types
        return JSONResponse(content=dumps(teams_data), media_type="application/json")
    
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)