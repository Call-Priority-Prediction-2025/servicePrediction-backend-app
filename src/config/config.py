from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Config(BaseSettings):
    selected_model_predictor: str = "testing.pkl"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", force_env_file=True
    )


@lru_cache
def get_config():
    return Config()


def reload_config():
    get_config.cache_clear()
    return get_config()


get_config.cache_clear()
