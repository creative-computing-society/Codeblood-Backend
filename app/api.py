from fastapi import FastAPI, HTTPException
from schemas import Team
from mongo import teams_collection, mail_collection

app = FastAPI()

@app.post("/register", response_model=Team)
async def register_team(team: Team):
    #Check if team with same name already exists
    existing_team = await teams_collection.find_one({"team_name": team.team_name})
    if existing_team:
        raise HTTPException(status_code=400, detail="Team with this name already exists")

    
    #Add team to the database
    stored_team=await teams_collection.insert_one(team.model_dump)


    team_id= stored_team.inserted_id

    mails=[player.player_mail for player in team.players]

    # Add participant emails to the database
    for mail in mails:
        await mail_collection.insert_one({"team_id": team_id, "email": mail})

    return f"{team.team_name} has been registered successfully."
