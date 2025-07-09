from pydantic import BaseModel


class RegisterTeam(BaseModel):
    team_name: str
    username: str
    is_hacker: bool
    is_wizard: bool


class JoinTeam(BaseModel):
    team_code: str
    username: str
    is_hacker: bool
    is_wizard: bool
