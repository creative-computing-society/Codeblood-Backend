from pydantic import BaseModel


class Team(BaseModel):
    team_name: str
    points: int = 0
    powerups: list[str] = []

