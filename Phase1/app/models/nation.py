from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Nation(BaseModel):
    nation_id: str
    name: str
    captured: bool = False
    captured_by: Optional[str] = None
    timestamp: Optional[datetime] = None
    points: int = 100