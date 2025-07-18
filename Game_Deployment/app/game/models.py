from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

class Player(BaseModel):
    user_name: str
    team_code: str
    Status: List[int] = Field(..., min_items=7, max_items=7)  # 7 levels, each with a status

class Lobby(BaseModel):
    lobby_id: str
    team_code: str
    players: List[dict]  # Each player is a dictionary with player details

class Points(BaseModel):
    team_code: str
    team_name: str
    Question_solved: int = 0
    Levels_Cleared: int = 0
    Current_level: int = 0
    Points: int = 0
    Current_Level_Entered_At: Optional[datetime] = None
    Total_Time_To_Clear_Levels: float = 0.0