from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, asc
from fastapi import HTTPException
import uuid

import env
import models
import tablename_hasher
from models import ChatSession, multi_turn_default_count


def get_room_list(user_email: str, db: Session):
    return db.query(ChatSession)\
    .filter(
        ChatSession.user_email == user_email,
        ChatSession.is_deleted == False
    ).order_by(
        desc(ChatSession.id)
    ).all()


def read_multi_turn(user_email: str, session_id: str, db: Session):
    if session_id == 'new':
        new_db_multi_turn = ChatSession(user_email=user_email, session_id=str(uuid.uuid4()))
        db.add(new_db_multi_turn)
        db.commit()
        db.refresh(new_db_multi_turn)
        return new_db_multi_turn
    else:
        db_chat_session = db.query(ChatSession).filter(
            and_(
                ChatSession.user_email == user_email,
                ChatSession.session_id == session_id,
                ChatSession.is_deleted == False
            )
        ).first()
        if db_chat_session is None:
            raise HTTPException(status_code=404, detail="ChatSession not found")
        else:
            return db_chat_session


# user_email과 session_id로 multi_turn_count를 확인 후
# if 세팅값(multi_turn_count)보다 작으면 +1 하고 +1 하기 전 값 리턴
# else 세팅값과 같으면 db 값 그대로 리턴
def read_before_and_update_multi_turn_count(user_email: str, session_id: str, db: Session):
    db_chat_session = db.query(ChatSession)\
        .filter(
            and_(
                ChatSession.user_email == user_email,
                ChatSession.session_id == session_id,
                ChatSession.is_deleted == False
            )
        ).first()
    ## db에 없는 경우 신규대화
    if db_chat_session is None:
        new_db_multi_turn = ChatSession(user_email=user_email, session_id=session_id)
        db.add(new_db_multi_turn)
        db.commit()
        db.refresh(new_db_multi_turn)
        return new_db_multi_turn.multi_turn_count
    if db_chat_session.multi_turn_count < env.multi_turn_default_count:
        db_chat_session.multi_turn_count = db_chat_session.multi_turn_count + 1
        db.commit()
        db.refresh(db_chat_session)
        return db_chat_session.multi_turn_count - 1
    else:
        return db_chat_session.multi_turn_count


def update_multi_turn_count(user_email: str, session_id: str, db: Session):
    db_chat_session = db.query(ChatSession).filter(
        and_(
            ChatSession.user_email == user_email,
            ChatSession.session_id == session_id,
            ChatSession.is_deleted == False
        )
    ).first()
    if db_chat_session is None:
        raise HTTPException(status_code=404, detail="ChatSession not found")
    db_chat_session.multi_turn_count = db_chat_session.multi_turn_count + 1 \
        if db_chat_session.multi_turn_count < multi_turn_default_count else db_chat_session.multi_turn_count
    db.commit()
    db.refresh(db_chat_session)
    return db_chat_session


def refresh_multi_turn_count(user_email: str, session_id: str, db: Session):
    db_chat_session = db.query(ChatSession).filter(
        and_(
            ChatSession.user_email == user_email,
            ChatSession.session_id == session_id,
            ChatSession.is_deleted == False
        )
    ).first()
    if db_chat_session is None:
        raise HTTPException(status_code=404, detail="ChatSession not found")
    db_chat_session.multi_turn_count = 0
    db.commit()
    db.refresh(db_chat_session)
    return db_chat_session


def get_room_history(user_email: str, session_id: str, db: Session):
    tb_name = tablename_hasher.get_sharding_tb_name(user_email)
    chat_history_entity = models.create_chat_history_entity(tb_name)
    chat_history_entity_list = db.query(chat_history_entity)\
        .filter(
            and_(
                chat_history_entity.user_email == user_email,
                chat_history_entity.session_id == session_id
            )
        ).order_by(
            asc(chat_history_entity.created_at)
        ).all()
    # return chat_history_entity_list
    if len(chat_history_entity_list) > 0:
        return models.map_to_chat_message_dto(chat_history_entity_list)
    else:
        return []




def delete_chat(user_email: str, session_id: str, db: Session):
    db_chat_session = db.query(ChatSession).filter(
        and_(
            ChatSession.user_email == user_email,
            ChatSession.session_id == session_id,
            ChatSession.is_deleted == False
        )
    ).first()
    if db_chat_session is None:
        raise HTTPException(status_code=404, detail="ChatSession not found")
    db_chat_session.is_deleted = True
    db.commit()
    db.refresh(db_chat_session)
    return db_chat_session
