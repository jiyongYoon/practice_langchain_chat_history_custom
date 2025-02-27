import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from chat_session_services import *
from stream_services import *
from models import ChatSessionDto, QuestionRequest, ChatMessageDto, MessageDto, ChatDeleteRequest


chat_router = APIRouter()


@chat_router.get("/chats/{user_email}/room", response_model=List[ChatSessionDto])
async def room_list(user_email: str, db: Session = Depends(get_db)):
    return get_room_list(user_email, db)


@chat_router.get("/chats/{user_email}/rooms/{session_id}/multi-count", response_model=ChatSessionDto)
async def read(user_email: str, session_id: str, db: Session = Depends(get_db)):
    return read_multi_turn(user_email, session_id, db)


@chat_router.post("/chats/{user_email}/rooms/{session_id}/multi-count", response_model=ChatSessionDto)
async def chat(user_email: str, session_id: str, db: Session = Depends(get_db)):
    return update_multi_turn_count(user_email, session_id, db)


@chat_router.post("/chats/{user_email}/rooms/{session_id}/multi-refresh")
async def refresh(user_email: str, session_id: str, db: Session = Depends(get_db)):
    user_message, ai_message = insert_refresh_history(user_email, session_id)
    timestamp = datetime.datetime.now()
    user_message = MessageDto(
        data=str(user_message),
        type="human",
        created_at=timestamp
    )
    ai_message = MessageDto(
        data=str(ai_message),
        type="ai",
        created_at=timestamp
    )
    db_chat_session = refresh_multi_turn_count(user_email, session_id, db)
    return ChatMessageDto(
        id=db_chat_session.id,
        user_email=db_chat_session.user_email,
        session_id=db_chat_session.session_id,
        message=[user_message, ai_message]
    )


@chat_router.get("/chats/{user_email}/rooms/{session_id}")
async def room_history(user_email: str, session_id: str, db: Session = Depends(get_db)):
    return get_room_history(user_email, session_id, db)


@chat_router.delete("/chats/{user_email}/rooms/{session_id}", response_model=ChatSessionDto)
async def delete(user_email: str, session_id: str, db: Session = Depends(get_db)):
    return delete_chat(user_email, session_id, db)


@chat_router.delete("/chats")
async def delete_chats(chat_delete_request: ChatDeleteRequest, db: Session = Depends(get_db)):
    return delete_all_chats_by_user_email(
        user_email=chat_delete_request.user_email,
        batch_size=3,
        db=db
    )


rag_router = APIRouter()


@rag_router.post("/chats/{user_email}/rooms/{session_id}/stream")
async def stream(user_email: str, session_id: str, question_request: QuestionRequest, db: Session = Depends(get_db)):
    db_session_id = chain_stream(user_email, session_id, question_request.question, db)
    return update_multi_turn_count(user_email, db_session_id, db)
