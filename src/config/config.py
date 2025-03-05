from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Config(BaseSettings):
    selected_model_predictor: str = "testing.pkl"

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_config():
    return Config()