from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from chat_session_services import *
from stream_services import *
from models import ChatSessionDto, QuestionRequest


chat_router = APIRouter()


@chat_router.get("/chats/{user_email}/room", response_model=List[ChatSessionDto])
async def room_list(user_email: str, db: Session = Depends(get_db)):
    return get_room_list(user_email, db)


@chat_router.get("/chats/{user_email}/rooms/{session_id}/multi_count", response_model=ChatSessionDto)
async def read(user_email: str, session_id: str, db: Session = Depends(get_db)):
    return read_multi_turn(user_email, session_id, db)


@chat_router.post("/chats/{user_email}/rooms/{session_id}/multi_count", response_model=ChatSessionDto)
async def chat(user_email: str, session_id: str, db: Session = Depends(get_db)):
    return update_multi_turn_count(user_email, session_id, db)


@chat_router.post("/chats/{user_email}/rooms/{session_id}/multi_refresh", response_model=ChatSessionDto)
async def refresh(user_email: str, session_id: str, db: Session = Depends(get_db)):
    insert_refresh_history(user_email, session_id)
    return refresh_multi_turn_count(user_email, session_id, db)


@chat_router.get("/chats/{user_email}/rooms/{session_id}")
async def room_history(user_email: str, session_id: str, db: Session = Depends(get_db)):
    return get_room_history(user_email, session_id, db)


@chat_router.delete("/chats/{user_email}/rooms/{session_id}", response_model=ChatSessionDto)
async def delete(user_email: str, session_id: str, db: Session = Depends(get_db)):
    return delete_chat(user_email, session_id, db)


rag_router = APIRouter()


@rag_router.post("/chats/{user_email}/rooms/{session_id}/stream")
async def stream(user_email: str, session_id: str, question_request: QuestionRequest, db: Session = Depends(get_db)):
    db_session_id = chain_stream(user_email, session_id, question_request.question, db)
    return update_multi_turn_count(user_email, db_session_id, db)
