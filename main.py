from dotenv import load_dotenv

load_dotenv()


from fastapi import FastAPI
from db import engine, Base
from routes import chat_router, rag_router

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# create tables
Base.metadata.create_all(bind=engine)

##### api 세팅 #####

app.include_router(chat_router)
app.include_router(rag_router)

##### langserve 세팅 #####

from langserve import add_routes
from stream_services import get_chain_with_history
from chain_config_def import fetch_header

chain_with_history = get_chain_with_history()

add_routes(
    app=app,
    runnable=chain_with_history,
    path='/langserve/chat',
    playground_type="default",
    per_req_config_modifier=fetch_header
)