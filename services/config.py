import os
from typing import Optional
from dotenv import load_dotenv


class Settings():
    load_dotenv()
    rule34_url: Optional[str] = os.getenv("RULE34_URL")
    danbooru_url: Optional[str] = os.getenv("DANBOORU_URL")
    safebooru_url: Optional[str] = os.getenv("SAFEBOORU_URL")
    konachan_url: Optional[str] = os.getenv("KONACHAN_URL")
    bot_token: str = os.getenv("BOT_TOKEN")


settings = Settings()
