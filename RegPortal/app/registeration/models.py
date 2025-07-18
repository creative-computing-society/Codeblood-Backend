from typing import List
from pydantic import BaseModel, EmailStr, field_validator
import re


class RegisterTeam(BaseModel):
    team_name: str
    username: str
    discord_id: str
    rollno: str  # Correct field name to match frontend key

    @field_validator("team_name")
    @classmethod
    def validate_team_name(cls, team_name):
        if not re.match(r"^[\w ]{1,20}$", team_name):
            raise ValueError("Invalid team name format")
        return team_name

    @field_validator("username", "discord_id")
    @classmethod
    def validate_username_and_discord_id(cls, value):
        if not re.match(r"^[a-zA-Z0-9._]{2,32}$", value):
            raise ValueError(
                "Invalid Discord username. Use 2–32 characters (letters, numbers, dots, underscores)."
            )
        return value

    @field_validator("rollno")  # Ensure the decorator references the correct field
    @classmethod
    def validate_rollno(cls, rollno):
        if not re.match(r"^\d{4,12}$", rollno):
            raise ValueError("Invalid roll number format")
        return rollno

class JoinTeam(BaseModel):
    team_code: str
    username: str
    discord_id: str
    rollno: str  # Correct field name to match frontend key

    @field_validator("username", "discord_id")
    @classmethod
    def validate_username_and_discord_id(cls, value):
        if not re.match(r"^[a-zA-Z0-9._]{2,32}$", value):
            raise ValueError(
                "Invalid Discord username. Use 2–32 characters (letters, numbers, dots, underscores)."
            )
        return value

    @field_validator("rollno")  # Ensure the decorator references the correct field
    @classmethod
    def validate_rollno(cls, rollno):
        if not re.match(r"^\d{4,12}$", rollno):
            raise ValueError("Invalid roll number format")
        return rollno

class Player(BaseModel):
    name: str
    id: str
    rollno: str  # Add rollno field
    email: EmailStr
    is_hacker: bool
    is_wizard: bool
    discord_id: str  # Add this field

    @field_validator("is_wizard")
    @classmethod
    def check_complementary_roles(cls, is_wizard, info):
        is_hacker = info.data.get("is_hacker")
        if is_hacker is None:
            raise ValueError("is_hacker must be provided")

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


class LeaveTeamRequest(BaseModel):
    email: str  

class RemoveFromTeamRequest(BaseModel):
    email_to_remove: str