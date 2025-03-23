from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(override=True)


class Config(BaseSettings):
    openai_api_key: str
    openai_base_url: str
    openai_model: str

    class Config:
        env_file = ".env"


config = Config()
