from typing import Dict, Any

from fastapi import Request, HTTPException

from chat_session_services import read_before_and_update_multi_turn_count
from env import multi_turn_default_count
from db import get_db


# rag chain config
configurable_string = "configurable"
user_email_config_fields = "user_email"
session_id_config_fields = "session_id"
window_size_config_fields = "window_size"


def fetch_header(config: Dict[str, Any], req: Request) -> Dict[str, Any]:
    db = next(get_db())

    try:
        if configurable_string not in config:
            config[configurable_string] = {}

        if user_email_config_fields in req.headers:
            config[configurable_string][user_email_config_fields] = req.headers[user_email_config_fields]
        else:
            config[configurable_string][user_email_config_fields] = 'anony-user'

        if session_id_config_fields in req.headers:
            config[configurable_string][session_id_config_fields] = req.headers[session_id_config_fields]
            if req.headers[session_id_config_fields] != "new":
                header_email = config[configurable_string][user_email_config_fields]
                header_session_id = config[configurable_string][session_id_config_fields]
                config[configurable_string][window_size_config_fields] = read_before_and_update_multi_turn_count(
                    user_email=header_email,
                    session_id=header_session_id,
                    db=db
                )
            else:
                config[configurable_string][window_size_config_fields] = multi_turn_default_count
        else:
            print(session_id_config_fields + " required!!")
            raise HTTPException(status_code=400, detail=session_id_config_fields + " required!!")

        print(f"===> configurable: {config}")
        return config
    finally:
        db.close()
