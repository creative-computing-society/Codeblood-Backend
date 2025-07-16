import loggers
import os
import uvicorn
import asyncio

from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from logging import getLogger
from json import load

from app.db.mongo import teams_col, users_col, mail_sent_col, db
from app.utils.mailer import send_mail
from app.routes.discord_bot import router
from discord_bot import init_bot, TeamChannels

from fastapi import BackgroundTasks

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
logger = getLogger(__name__)

bot = init_bot()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async def start_bot():
        if DISCORD_BOT_TOKEN is None:
            raise RuntimeError("Discord bot token not found!")

        await bot.start(DISCORD_BOT_TOKEN)

    logger.info("Bot is up!")
    asyncio.create_task(start_bot())
    yield

    await bot.close()
    logger.info("Bot has been shut down")


app = FastAPI(lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))
app.include_router(router)

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
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": "Invalid credentials"}
    )


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)


# ------------------- DASHBOARD -------------------
@app.get("/dashboard")
async def dashboard(request: Request):
    now = datetime.now()

    # Run Mongo queries in parallel
    teams_task = teams_col.find().to_list(None)
    users_task = users_col.find().to_list(None)
    mails_task = mail_sent_col.find().to_list(None)

    teams, all_users, mail_records = await asyncio.gather(
        teams_task, users_task, mails_task
    )

    # Sort and filter
    recent_teams = sorted(teams, key=lambda t: t.get("_id"), reverse=True)[:5]

    team_counts = {i: 0 for i in range(1, 5)}
    for team in teams:
        team_counts[len(team["players"])] += 1

    team_user_emails = set(p["email"] for t in teams for p in t["players"])
    users_without_teams = [
        u["email"] for u in all_users if u["email"] not in team_user_emails
    ]

    mail_map = {m["team_code"]: m["last_mailed_at"] for m in mail_records}
    for team in teams:
        team["last_mailed_at"] = mail_map.get(team["team_code"])

    def sort_key(team):
        mailed_at = team.get("last_mailed_at")
        if mailed_at and (now - mailed_at) < timedelta(hours=10):
            return (1, mailed_at)
        return (0, None)

    teams_sorted = sorted(teams, key=sort_key)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "team_counts": team_counts,
            "recent_teams": recent_teams,
            "users_without_teams": users_without_teams,
            "all_teams": teams_sorted,
            "now": now,
        },
    )


# ------------------- DASHBOARD DATA (AJAX) -------------------
@app.get("/dashboard-data")
async def dashboard_data():
    teams = await teams_col.find().to_list(None)

    team_counts = {i: 0 for i in range(1, 5)}
    for team in teams:
        size = len(team.get("players", []))
        team_counts[size] = team_counts.get(size, 0) + 1

    recent_teams = sorted(teams, key=lambda x: x.get("_id", 0), reverse=True)[:5]
    recent_data = [
        {"team_name": t["team_name"], "team_leader_email": t["team_leader_email"]}
        for t in recent_teams
    ]

    users = await users_col.find().to_list(None)
    users_with_teams = set(u.get("email") for u in users if u.get("team_id"))
    users_all = set(u.get("email") for u in users)
    users_without_teams = list(users_all - users_with_teams)

    return JSONResponse(
        {
            "total_teams": len(teams),
            "team_counts": team_counts,
            "recent_teams": recent_data,
            "users_without_teams": users_without_teams,
        }
    )


# ------------------- SEND MAIL -------------------
@app.get("/send-mail/{team_code}")
async def send_mail_to_team(team_code: str):
    team = await teams_col.find_one({"team_code": team_code})
    if not team or len(team["players"]) == 4:
        return RedirectResponse("/dashboard")

    for player in team["players"]:
        send_mail(
            to_email=player["email"],
            subject="⏳ Complete your team for Obscura!",
            name=player["name"],
            team_name=team["team_name"],
        )

    await mail_sent_col.update_one(
        {"team_code": team_code},
        {"$set": {"last_mailed_at": datetime.utcnow()}},
        upsert=True,
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
            continue  # skip if mailed recently

        for player in team["players"]:
            background_tasks.add_task(
                send_mail,
                to_email=player["email"],
                subject="⏳ Complete your team for Obscura!",
                name=player["name"],
                team_name=team["team_name"],
            )

        await mail_sent_col.update_one(
            {"team_code": team["team_code"]},
            {"$set": {"last_mailed_at": datetime.utcnow()}},
            upsert=True,
        )

    return RedirectResponse("/dashboard", status_code=302)


# --------------------BOT TESTING----------------
@app.get("/fuck")
async def create_channels(request: Request):
    with open("test.json") as file:
        data = load(file)

        team_channels = TeamChannels(bot)
        await team_channels.create_channels(data)
        logger.info(team_channels.invalid_ids)


# ------------------- UVICORN -------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=2130, reload=True)
