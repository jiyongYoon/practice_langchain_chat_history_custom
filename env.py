import os

from dotenv import load_dotenv

load_dotenv()

multi_turn_default_count = int(os.environ["MULTI_TURN_DEFAULT_COUNT"])
context_refresh_ai_message = os.environ["CONTEXT_REFRESH_AI_MESSAGE"]

username = os.environ["POSTGRES_DB_USERNAME"]
password = os.environ["POSTGRES_DB_PASSWORD"]
host = os.environ["POSTGRES_DB_HOST"]
port = os.environ["POSTGRES_DB_PORT"]
db_name = os.environ["POSTGRES_DB_NAME"]

connection_path = f"postgresql://{username}:{password}@{host}:{port}/{db_name}"
