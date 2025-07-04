from pydantic import BaseModel, EmailStr
from uuid import UUID


class Player(BaseModel):
    player_name: str
    player_mail: EmailStr
    player_phone: str
    
    
    
class Team(BaseModel):
    team_name: str
    players: list[Player]
    player_count: int
    join_code: str


# This schema is used to store the email of participants along with their team id which is Mongo's _id field.
class users(BaseModel):
    team_id: UUID
    email: str
    progress: list[int] = [0] * 25
