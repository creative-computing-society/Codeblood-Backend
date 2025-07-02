from fastapi import APIRouter

router = APIRouter()


@router.get("/usernames")
async def user_names():
    """
    Gets all the usernames of the selected participants
    """
    pass
