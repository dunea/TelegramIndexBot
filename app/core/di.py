from injector import Injector, Module, provider, singleton
from sqlalchemy.orm import Session, scoped_session
from app.core.database import Database
from app.core.meilisearch import MeiliSearch
from app.core.settings import settings
from app.core.tme_scraper import TmeScraper


class DatabaseProvider(Module):
    @singleton
    @provider
    def provide_session(self) -> scoped_session[Session]:
        return Database(
            settings.DB_USER,
            settings.DB_PASSWORD,
            settings.DB_IP,
            settings.DB_PORT,
            settings.DB_NAME,
        ).session


class MeiliSearchProvider(Module):
    @singleton
    @provider
    def provide_session(self) -> MeiliSearch:
        return MeiliSearch(
            url=settings.MEILISEARCH_API_URL,
            api_key=settings.MEILISEARCH_API_KEY,
        )


class TmeScraperProvider(Module):
    @singleton
    @provider
    def provide_session(self) -> TmeScraper:
        return TmeScraper(token=settings.SMARTDAILI_SCRAPER_TOKEN)


# 创建 Injector 实例并注入依赖
di = Injector([DatabaseProvider(), MeiliSearchProvider(), TmeScraperProvider()])
