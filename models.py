import datetime
import uuid
from typing import Optional, Dict, Any, List

from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Boolean, Uuid, JSON
from pydantic import BaseModel, UUID4

from db import Base
from env import multi_turn_default_count
from singleton_store import _chat_history_entity_cache


class ChatSession(Base):
    __tablename__ = 'chat_session'

    id = Column(BigInteger, nullable=False, primary_key=True)
    user_email = Column(String(100), nullable=False)
    session_id = Column(Uuid, nullable=False, default=uuid.uuid4)
    multi_turn_count = Column(Integer, nullable=False, default=multi_turn_default_count)
    create_at = Column(DateTime, nullable=False, default=datetime.datetime.now)
    is_deleted = Column(Boolean, nullable=False, default=False)


class ChatSessionDto(BaseModel):
    id: int
    user_email: str
    session_id: UUID4
    multi_turn_count: int
    create_at: datetime.datetime
    is_deleted: bool

    class Config:
        from_attributes = True


class QuestionRequest(BaseModel):
    question: str


## 실제 저장되는 json 데이터 스키마 그대로
# class MessageContentDto(BaseModel):
#     id: Optional[str] = None
#     name: Optional[str] = None
#     type: str
#     content: str
#     example: bool
#     additional_kwargs: Dict[str, Any] = {}
#     response_metadata: Dict[str, Any] = {}


class MessageDto(BaseModel):
    data: str # 원래는 MessageContentDto가 들어가야하나, 커스텀함
    type: str
    created_at: datetime.datetime


class ChatMessageDto(BaseModel):
    id: int
    user_email: str
    session_id: UUID4
    message: List[MessageDto]


def create_chat_history_entity(table_name):
    if table_name not in _chat_history_entity_cache:
        class ChatHistoryEntity(Base):
            __tablename__ = table_name

            id = Column(BigInteger, nullable=False, primary_key=True)
            user_email = Column(String(100), nullable=False)
            session_id = Column(Uuid, nullable=False, default=uuid.uuid4)
            message = Column(JSON, nullable=False)
            created_at = Column(DateTime, nullable=False)

        _chat_history_entity_cache[table_name] = ChatHistoryEntity

    return _chat_history_entity_cache[table_name]


def map_to_chat_message_dto(chat_history_entity_list: List):
    message_dtos = []
    for entity in chat_history_entity_list:
        message_dto = MessageDto(
            data=str(entity.message['data']['content']),
            type=entity.message['type'],
            created_at=entity.created_at
        )
        message_dtos.append(message_dto)

    return ChatMessageDto(
        id=chat_history_entity_list[0].id,
        user_email=chat_history_entity_list[0].user_email,
        session_id=chat_history_entity_list[0].session_id,
        message=message_dtos,
    )
