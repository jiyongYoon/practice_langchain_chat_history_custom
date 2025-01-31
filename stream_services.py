from sqlalchemy.orm import Session
from langchain_core.runnables.utils import ConfigurableFieldSpec
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

import env
from custom_chat_message_histories import MyPostgresChatMessageHistory
from db import initialize_sync_connection
from tablename_hasher import get_sharding_tb_name
from chat_session_services import read_multi_turn


def get_chat_history(user_email: str, session_id: str, window_size: int = None):
    table_name = get_sharding_tb_name(user_email)
    sync_connection = initialize_sync_connection()
    return MyPostgresChatMessageHistory(
        table_name=table_name,
        user_email=user_email,
        session_id=session_id,
        window_size=window_size,
        sync_connection=sync_connection,
    )


def get_config_fields():
    return [
        ConfigurableFieldSpec(
            id="user_email",
            annotation=str,
            name="User Email",
            description="Unique identifier for a user.",
            default="",
            is_shared=True,
        ),
        ConfigurableFieldSpec(
            id="session_id",
            annotation=str,
            name="Conversation ID",
            description="Unique identifier for a conversation.",
            default="",
            is_shared=True,
        ),
        ConfigurableFieldSpec(
            id="window_size",
            annotation=str,
            name="Multiturn Count",
            description="Contain Conversation pair for multiturn.",
            default="",
            is_shared=True,
        ),
    ]


def get_chain_with_history():
    prompt = ChatPromptTemplate.from_messages(
        [
            # 시스템 메시지
            ("system", "You are a helpful assistant."),
            # 대화 기록을 위한 Placeholder
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),  # 질문
        ]
    )

    # chain 을 생성합니다.
    chain = prompt | ChatOpenAI(model_name="gpt-4o-mini") | StrOutputParser()

    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_chat_history,
        input_messages_key="question",
        history_messages_key="chat_history",
        history_factory_config=get_config_fields(),
    )

    return chain_with_history


def chain_stream(user_email: str, session_id: str, question: str, db: Session):
    db_chat_session = read_multi_turn(user_email, session_id, db)
    if session_id == 'new':
        session_id = str(db_chat_session.session_id)

    window_size = db_chat_session.multi_turn_count
    config = {"configurable":
                  {
                      "user_email": user_email,
                      "session_id": session_id,
                      "window_size": window_size
                  }
    }

    chain_with_history = get_chain_with_history()

    chain_with_history.invoke({"question": question}, config)

    return str(db_chat_session.session_id)


def insert_refresh_history(user_email: str, session_id: str):
    chat_history = get_chat_history(user_email, session_id)
    chat_history.add_user_message("")
    chat_history.add_ai_message(env.context_refresh_ai_message)


