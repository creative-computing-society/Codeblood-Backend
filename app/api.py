from fastapi import FastAPI, HTTPException
from schemas import Team
from mongo import teams_collection

app = FastAPI()

@app.post("/register", response_model=Team)
async def register_team(team: Team):
    #Check if team with same name already exists
    existing_team = await teams_collection.find_one({"team_name": team.team_name})
    if existing_team:
        raise HTTPException(status_code=400, detail="Team with this name already exists")

    team.team_id = await teams_collection.count_documents({}) + 1

    #Add team to the database
    await teams_collection.insert_one(team.model_dump)

    return f"{team.team_name} has been registered successfully."
