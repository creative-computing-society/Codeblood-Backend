from pydantic import BaseModel, EmailStr, field_validator
from bson import ObjectId


class Player(BaseModel):
    player_name: str
    player_mail: EmailStr
    player_phone: str

    @field_validator('player_mail')
    def validate_email(cls, v):
        if not v.endswith('@thapar.edu'):
            raise ValueError('Email must end with @thapar.edu')
        return v

    @field_validator('player_phone')
    def validate_phone(cls, v):
        if not v.isdigit() or len(v) != 10:
            raise ValueError('Phone number must be a 10-digit number')
        return v
    
    
    
class Team(BaseModel):
    team_name: str
    team_id: int
    players: list[Player]
    player_count: int

    @field_validator('player_count')
    def validate_player_count(cls, player_count, player_list):
        if 'players' in player_list and len(player_list['players']) != player_count:
            raise ValueError('Player count must match the number of players provided')
        return player_count
    


# This schema is used to store the email of participants along with their team id which is Mongo's _id field.
class ParticipantMails(BaseModel):

    team_id: ObjectId
    email: str
