from typing import List
from pydantic import BaseModel, EmailStr, field_validator


class RegisterTeam(BaseModel):
    team_name: str
    username: str


class JoinTeam(BaseModel):
    team_code: str
    username: str


class Player(BaseModel):
    name: str
    id: str
    email: EmailStr
    is_hacker: bool
    is_wizard: bool

    @field_validator("is_wizard")
    @classmethod
    def check_complementary_roles(cls, is_wizard, info):
        is_hacker = info.data.get("is_hacker")
        is_wizard = info.data.get("is_wizard")
        if is_hacker is None:
            raise ValueError("is_hacker must be provided")

        if is_wizard is None:
            raise ValueError("is_wizard must be provided")

        if is_hacker == is_wizard:
            raise ValueError(
                "Player must be either a hacker or a wizard, not both or neither"
            )
        return is_wizard

    def __getitem__(self, key: str):
        return getattr(self, key)


class TeamDashboard(BaseModel):
    team_code: str
    players: List[Player]
