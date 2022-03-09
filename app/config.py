from functools import lru_cache
from typing import Any
from typing import Dict

from common import VaultClient
from pydantic import BaseSettings
from pydantic import Extra
from starlette.config import Config

config = Config('.env')
SRV_NAMESPACE = config('APP_NAME', cast=str, default='service_notification')
CONFIG_CENTER_ENABLED = config('CONFIG_CENTER_ENABLED', cast=str, default='false')


def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == 'false':
        return {}
    else:
        return vault_factory()


def vault_factory() -> dict:
    vc = VaultClient(config('VAULT_URL'), config('VAULT_CRT'), config('VAULT_TOKEN'))
    return vc.get_from_vault(SRV_NAMESPACE)


class Settings(BaseSettings):
    version = '1.0.0'
    APP_NAME: str = 'service_notification'
    PORT: int = 5065
    HOST: str = '0.0.0.0'
    ENV: str = 'test'

    DB_USER: str
    DB_PWD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    def __init__(self):
        super().__init__()
        self.SQLALCHEMY_DATABASE_URI = (
            f'postgresql://{self.DB_USER}:{self.DB_PWD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return env_settings, load_vault_settings, init_settings, file_secret_settings


@lru_cache(1)
def get_settings():
    settings = Settings()
    return settings


ConfigClass = get_settings()