from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Template

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=getenv("MAIL_PASSWORD"),
    MAIL_FROM=getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
)

async def send_email(name: str, team_name: str, email: str, template_path: str):
    with open(template_path, "r") as file:
        template = Template(file.read())
    html_content = template.render(name=name, team_name=team_name)

    message = MessageSchema(
        subject="Team Registration Confirmation",
        recipients=[email],
        body=html_content,
        subtype="html",
    )

    fm = FastMail(conf)
    await fm.send_message(message)

@router.post("/create-team")
@limiter.limit("10/minute") 
async def register_team(
    request: Request, data: RegisterTeam, user=Depends(get_current_user)
):
    teams: AsyncIOMotorCollection = request.app.state.teams
    users: AsyncIOMotorCollection = request.app.state.users

    team_name = data.team_name
    player_name = data.username
    discord_id = data.discord_id
    rollno = data.rollno  # Use rollNo from frontend

    check_user_task = teams.find_one({"players.email": user["email"]})
    check_team_task = teams.find_one({"team_name": team_name})
    user_in_team, team_exists = await asyncio.gather(check_user_task, check_team_task)

    if user_in_team:
        return JSONResponse(
            {"error": "User has already joined a team!"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if team_exists:
        return JSONResponse(
            {"error": "Team already exists"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    team_info = generate_initial_team(team_name, player_name, user["email"], discord_id, rollno)
    team_info["players"][0]["rollno"] = rollno  # Add rollNo to the team leader

    try:
        await teams.insert_one(team_info)
        await add_teamid_to_user(request, team_info.get("team_code", ""), user["email"])

        # Send email
        await send_email(
            name=player_name,
            team_name=team_name,
            email=user["email"],
            template_path="/home/in-l-f3rj863/Downloads/Hari/Hari/Obscura_backend/app/registeration/TeamRegistration.html",
        )

        return JSONResponse({"team_code": team_info.get("team_code")})

    except DuplicateKeyError:
        return JSONResponse(
            {"error": "Team name already exists"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        logger.critical(f"CRITICAL ERROR: {e}")
        await teams.delete_one({"team_code": team_info.get("team_code")})
        return JSONResponse(
            {"error": "Internal Server Error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@router.post("/join-team")
@limiter.limit("10/minute") 
async def join_team(request: Request, data: JoinTeam, user=Depends(get_current_user)):
    teams: AsyncIOMotorCollection = request.app.state.teams

    team_code = data.team_code
    discord_id = data.discord_id
    rollno = data.rollno  # Use rollNo from frontend

    existing = await teams.find_one({"team_code": team_code})

    if not existing:
        return JSONResponse(
            {"error": "Team code invalid or player already in team"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    for player in existing.get("players", []):
        if player["email"] == user["email"]:
            return JSONResponse(
                {"error": "Player already in team"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    update_info = add_player(team_code, data.username, user["email"], discord_id, rollno)
    result = await teams.update_one(*update_info)

    await add_teamid_to_user(request, team_code, user["email"])

    if result.modified_count == 0:
        return JSONResponse(
            {"error": "Maximum team capacity has been reached!"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Send email
    await send_email(
        name=data.username,
        team_name=existing["team_name"],
        email=user["email"],
        template_path="/home/in-l-f3rj863/Downloads/Hari/Hari/Obscura_backend/app/registeration/TeamRegistration.html",
    )

    return JSONResponse({"success": True})