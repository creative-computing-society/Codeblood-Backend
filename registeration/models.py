from typing import Dict, List
from pydantic import BaseModel


class RegisterTeam(BaseModel):
    team_name: str
    username: str


class JoinTeam(BaseModel):
    team_code: str
    username: str


class TeamDashboard(BaseModel):
    team_code: str
    players: List[Dict[str, str | bool]]
