from fastapi import FastAPI, HTTPException
from schemas import Team
from mongo import teams_collection, users_collection
import random

app = FastAPI()

@app.post("/register", response_model=Team)
async def register_team(team: Team):
    

    team.join_code=generate_code(team.team_name)

    #Add team to the database
    stored_team=await teams_collection.insert_one(team.model_dump)



    team_id=stored_team.inserted_id

    mails=[player.player_mail for player in team.players]

    # Add participant emails to the database
    for mail in mails:
        await users_collection.insert_one({"team_id": team_id, "email": mail})

    return f"{team.team_name} has been registered successfully."

#To be replaced with Aargh's code
def generate_code(team_name: str) -> str:
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(random.choices(characters, k=6))

# Check if a team with the given name exists, True, if it exists, otherwise False
@app.get("/check_team/{team_name}")
async def check_team(team_name: str):
    existing_team= await teams_collection.find_one({"team_name": team_name})
    if existing_team:
        return True
    else:
        return False
    

