from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class BroadCastData(BaseModel):
    author: str
    content: str
    timestamp: str


@router.post("/test")
async def test(request: Request, data: BroadCastData):
    print(data)
