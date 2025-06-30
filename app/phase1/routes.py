from os import path
from fastapi import APIRouter, Response

router = APIRouter(prefix="/phase1", tags=["phase1"])


@router.get("/nusrat-sena")
async def get_traffic_log():
    file_path = path.join(path.dirname(__file__), "assets", "traffic.txt")
    assert path.exists(file_path), f"File not found, file_path = {file_path}"
    return Response(open(file_path).read())
