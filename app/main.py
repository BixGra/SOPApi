from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import playlists, users, websocket
from app.utils.config import get_settings
from app.utils.connection_manager import connection_manager
from app.utils.errors import SOPApiError


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    delay = 300
    scheduler.add_job(connection_manager.check_stale(delay), "interval", seconds=delay)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(playlists.router)
app.include_router(users.router)
app.include_router(websocket.router)


origins = get_settings().origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(SOPApiError)
async def exception_handler(request: Request, error: SOPApiError):
    return JSONResponse(
        status_code=error.status_code,
        content=error.json(),
    )


@app.get("/")
async def root():
    return "SOP Api"
