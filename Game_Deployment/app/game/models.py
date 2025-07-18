from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

class Player(BaseModel):
    user_name: str
    team_code: str
    email: EmailStr 
    is_hacker: bool = False  
    is_wizard: bool = False  
    Status: List[int] = Field(..., min_items=6, max_items=6) 

class Lobby(BaseModel):
    lobby_id: str
    team_code: str
    players: List[Player]  # Update to use the Player model for consistency

class Points(BaseModel):
    team_code: str
    team_name: str
    Question_solved: int = 0
    Levels_Cleared: int = 0
    Current_level: int = 0
    Points: int = 0
    Current_Level_Entered_At: Optional[datetime] = None
    Total_Time_To_Clear_Levels: float = 0.0