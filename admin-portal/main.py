from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from datetime import datetime, timedelta
import os
import uvicorn

from app.db.mongo import teams_col, users_col, mail_sent_col, db
from app.utils.mailer import send_mail

from fastapi import BackgroundTasks

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

def is_logged_in(request: Request):
    return request.session.get("logged_in", False)


# ------------------- AUTH -------------------
@app.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login_post(request: Request, uid: str = Form(...), password: str = Form(...)):
    admin_uid = os.getenv("ADMIN_UID")
    admin_pwd = os.getenv("ADMIN_PASSWORD")
    if uid == admin_uid and password == admin_pwd:
        request.session["logged_in"] = True
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)


# ------------------- DASHBOARD -------------------
@app.get("/dashboard")
async def dashboard(request: Request):
    teams = await teams_col.find().to_list(None)
    recent_teams = sorted(teams, key=lambda t: t.get("_id"), reverse=True)[:5]

    team_counts = {i: 0 for i in range(1, 5)}
    for team in teams:
        team_counts[len(team['players'])] += 1

    all_users = await users_col.find().to_list(None)
    team_user_emails = set(p["email"] for t in teams for p in t["players"])
    users_without_teams = [u["email"] for u in all_users if u["email"] not in team_user_emails]

    # Get mail history from mail_sent_col
    mail_records = await mail_sent_col.find().to_list(None)
    mail_map = {m["team_code"]: m["last_mailed_at"] for m in mail_records}
    now = datetime.utcnow()

    for team in teams:
        team["last_mailed_at"] = mail_map.get(team["team_code"])

    def sort_key(team):
        mailed_at = team.get("last_mailed_at")
        if mailed_at and (now - mailed_at) < timedelta(hours=10):
            return (1, mailed_at)
        return (0, None)

    teams_sorted = sorted(teams, key=sort_key)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "team_counts": team_counts,
        "recent_teams": recent_teams,
        "users_without_teams": users_without_teams,
        "all_teams": teams_sorted,
        "now": now
    })


# ------------------- DASHBOARD DATA (AJAX) -------------------
@app.get("/dashboard-data")
async def dashboard_data():
    teams = await teams_col.find().to_list(None)

    team_counts = {i: 0 for i in range(1, 5)}
    for team in teams:
        size = len(team.get("players", []))
        team_counts[size] = team_counts.get(size, 0) + 1

    recent_teams = sorted(teams, key=lambda x: x.get("_id", 0), reverse=True)[:5]
    recent_data = [{"team_name": t["team_name"], "team_leader_email": t["team_leader_email"]} for t in recent_teams]

    users = await users_col.find().to_list(None)
    users_with_teams = set(u.get("email") for u in users if u.get("team_id"))
    users_all = set(u.get("email") for u in users)
    users_without_teams = list(users_all - users_with_teams)

    return JSONResponse({
        "total_teams": len(teams),
        "team_counts": team_counts,
        "recent_teams": recent_data,
        "users_without_teams": users_without_teams
    })


# ------------------- SEND MAIL -------------------
@app.get("/send-mail/{team_code}")
async def send_mail_to_team(team_code: str):
    team = await teams_col.find_one({"team_code": team_code})
    if not team or len(team["players"]) == 4:
        return RedirectResponse("/dashboard")

    for player in team["players"]:
        send_mail(
            to_email=player["email"],
            subject="Complete Your Team for Obscura!",
            name=player["name"],
            team_name=team["team_name"],
            team_code=team_code  # Pass the team_code here
        )

    await mail_sent_col.update_one(
        {"team_code": team_code},
        {"$set": {"last_mailed_at": datetime.utcnow()}},
        upsert=True
    )

    return RedirectResponse("/dashboard", status_code=302)
# ------------------- BULK MAILING -------------------
@app.post("/bulk-mail")
async def bulk_mail(background_tasks: BackgroundTasks):
    teams = await teams_col.find().to_list(None)

    mail_records = await mail_sent_col.find().to_list(None)
    mail_map = {m["team_code"]: m["last_mailed_at"] for m in mail_records}
    now = datetime.utcnow()

    for team in teams:
        if len(team["players"]) == 4:
            continue

        last_mailed = mail_map.get(team["team_code"])
        if last_mailed and now - last_mailed < timedelta(hours=10):
            continue  # Skip if mailed recently

        for player in team["players"]:
            background_tasks.add_task(
                send_mail,
                to_email=player["email"],
                subject="Complete your Team for Obscura!",
                name=player["name"],
                team_name=team["team_name"],
                team_code=team["team_code"]  # Pass the team_code here
            )

        await mail_sent_col.update_one(
            {"team_code": team["team_code"]},
            {"$set": {"last_mailed_at": datetime.utcnow()}},
            upsert=True
        )

    return RedirectResponse("/dashboard", status_code=302)

# ------------------- UVICORN -------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=2130, reload=True)
