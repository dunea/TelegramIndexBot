from injector import Injector, Module, provider, singleton
from sqlalchemy.orm import Session, scoped_session
from app.core.database import Database
from app.core.settings import settings


class DatabaseProvider(Module):
    @singleton
    @provider
    def provide_session(self) -> scoped_session[Session]:
        return Database(
            settings.DB_USER,
            settings.DB_PASSWORD,
            settings.DB_HOST,
            settings.DB_PORT,
            settings.DB_NAME,
        ).session


# 创建 Injector 实例并注入依赖
di = Injector([DatabaseProvider()])
