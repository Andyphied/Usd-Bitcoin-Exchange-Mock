from logging import DEBUG
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic import BaseSettings, AnyHttpUrl
from pydantic.networks import EmailStr

path = Path.cwd()

env_path = path / '.env'

load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    # API_V1_STR: str = "/api/v1"
    API_TITLE: str = os.environ.get("API_TITLE", "TaskSubstrata")
    API_V1_0STR: str = "/v1_0"
    USD_LIMIT: float = os.environ.get("USD_LIMIT", 999999)
    BITCOIN_LIMIT: float = os.environ.get("BITCOIN_LIMIT", 100)


# To do, ask the signnifcance of some of these variables.

settings = Settings()
