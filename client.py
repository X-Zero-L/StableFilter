from openai import AsyncOpenAI
from config import config

openai_client = AsyncOpenAI(
    api_key=config.openai_api_key,
    base_url=config.openai_base_url
)