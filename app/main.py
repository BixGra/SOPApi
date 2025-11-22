from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import playlists
from app.utils.errors import SOPApiError


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(playlists.router)


origins = ["*"]

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
