from fastapi import FastAPI
from app import models, database
from app.routers import conversation

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="BOT GPT Backend")

app.include_router(conversation.router)

@app.get("/")
def home():
    return {"message": "BOT GPT API is ready"}