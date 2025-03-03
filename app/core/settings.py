import os
from typing import Optional

from pydantic.v1 import Field
from pydantic_settings import BaseSettings

from app.core.logger import logger


class Settings(BaseSettings):
    # 机器人
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    WEBHOOK_SECRET: Optional[str] = None
    WEBHOOK_URL: Optional[str] = None
    WEBHOOK_PORT: int = 5000
    WEBHOOK_HOST: str = '0.0.0.0'
    
    # 数据库
    DB_IP: str = Field(..., env="DB_IP")
    DB_PORT: int = 3306
    DB_USER: str = Field(..., env="DB_USER")
    DB_PASSWORD: str = Field(..., env="DB_PASSWORD")
    DB_NAME: str = Field(..., env="DB_NAME")
    
    # MeiliSearch
    MEILISEARCH_API_KEY: str = Field(..., env="MEILISEARCH_API_KEY")
    MEILISEARCH_API_URL: str = Field(..., env="MEILISEARCH_API_URL")
    
    # Smartdaili
    SMARTDAILI_SCRAPER_TOKEN: str = Field(..., env="SMARTDAILI_SCRAPER_TOKEN")
    
    # Api
    API_KEY: str = Field(..., env="API_KEY")
    
    class Config:
        env_file = ".env"  # 指定 .env 文件路径
        env_file_encoding = 'utf-8'


settings = Settings()
