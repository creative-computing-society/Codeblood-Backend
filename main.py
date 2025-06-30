from app import phase1_router
from fastapi import FastAPI
from uvicorn import run

app = FastAPI()
app.include_router(phase1_router)

if __name__ == "__main__":
    run(app)
