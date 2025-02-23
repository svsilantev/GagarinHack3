from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from config import config
from src.database.db import init_models

app: FastAPI = FastAPI()

# app.mount("/media", StaticFiles(directory="media"), name="media")

origins = [
    'http://localhost',
    'http://localhost:8080',
    'http://localhost:3000',
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.on_event('startup')
async def startup():
    if config.reset_db:
        await init_models()
        print('database reseted')

