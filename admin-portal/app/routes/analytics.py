from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.db.mongo import db
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/analytics", response_class=HTMLResponse)
async def get_analytics(request: Request):
    teams_cursor = db["teams"].find()
    teams = await teams_cursor.to_list(None)

    size_count = {1:0, 2:0, 3:0, 4:0}
    for team in teams:
        size = len(team.get("players", []))
        if size in size_count:
            size_count[size] += 1

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "team_counts": size_count,
        "total_teams": len(teams)
    })