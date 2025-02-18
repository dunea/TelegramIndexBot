import re
from datetime import datetime, timezone
from typing import Optional

from injector import inject
from sqlalchemy.orm import Session, scoped_session

from app import models, schemas
from app.core.logger import logger
from app.core.meilisearch import MeiliSearch
from app.core.tme_scraper import TmeScraper
from app.schemas import TmeIndexBase


class IndexService:
    @inject
    def __init__(self, session: scoped_session[Session], meilisearch: MeiliSearch, tme_scraper: TmeScraper):
        self.session = session
        self.meilisearch = meilisearch
        self.tme_scraper = tme_scraper
    
    # 添加索引用户名
    def add_index_by_tme(self, username: str) -> schemas.TmeIndexBase:
        if len(username) < 4 or len(username) > 32:
            logger.debug(f"用户名长度为4 ~ 32个字符: {username}")
            raise ValueError("用户名长度为4 ~ 32个字符")
        
        with self.session() as session:
            # 查询
            try:
                index_ = session.query(models.TmeIndex).filter(models.TmeIndex.username == username).one_or_none()
            except Exception as e:
                logger.error(f"查询索引发生错误: {e}")
                raise Exception("查询索引发生错误")
            if index_ is not None:
                try:
                    return schemas.TmeIndexBase.model_validate(index_)
                except Exception as e:
                    logger.error(f"序列化索引发生错误: {e}")
                    raise Exception("序列化索引发生错误")
        
        tme_info = self.tme_scraper.get_tme_info(username)
        if tme_info.type == "invalid":
            logger.debug(f"无法进行查询或不存在: {username}")
            raise ValueError("无法进行查询或不存在")
        elif tme_info.type == "user":
            logger.debug(f"暂不支持收录用户索引: {username}")
            raise ValueError("暂不支持收录用户索引")
        elif tme_info.type == "group":
            tme_type = models.TmeIndexType.GROUP
        elif tme_info.type == "channel":
            tme_type = models.TmeIndexType.CHANNEL
        elif tme_info.type == "bot":
            tme_type = models.TmeIndexType.BOT
        else:
            logger.debug(f"不支持的收录类型: {username}")
            raise ValueError("不支持的收录类型")
        
        with Session() as session:
            # 添加
            try:
                index = models.TmeIndex(
                    username=username,
                    nickname=tme_info.nickname,
                    desc=tme_info.description,
                    type=tme_type,
                    last_gather_at=datetime.now(timezone.utc),
                )
                session.add(index)
                session.commit()
                session.refresh(index)
            except Exception as e:
                logger.error(f"添加到数据库发生错误: {e}")
                raise Exception("添加到数据库发生错误")
            
            try:
                index_schema = schemas.TmeIndexBase.model_validate(index)
                self.meilisearch.index.add_documents([index_schema.model_dump(mode='json')], primary_key="id")
            except Exception as e:
                session.rollback()
                logger.error(f"添加到搜索引擎发生错误: {e}")
                raise Exception("添加到搜索引擎发生错误")
        
        return index_schema
    
    # 添加索引链接
    def add_index_by_tme_link(self, tme_link: str) -> schemas.TmeIndexBase:
        # 正则获取tme_link
        usernames = []
        pattern = r"url='https://t.me/([^/?')]{3,32})"
        matches = re.findall(pattern, tme_link)
        if matches:
            for item in matches:
                if len(item) > 0:
                    usernames.append(item)
        if len(usernames) == 0:
            logger.debug(f"未检测到有效的Telegram链接: {tme_link}")
            raise ValueError("未检测到有效的Telegram链接")
        if len(usernames) > 1:
            logger.debug(f"每次仅能添加1个Telegram链接: {tme_link}")
            raise ValueError("每次仅能添加1个Telegram链接")
        
        return self.add_index_by_tme(usernames[0])
    
    # 搜索索引
    def search_index(self, keywords: str, _type: models.TmeIndexType, page: int = 1,
                     limit: int = 20) -> schemas.TmeIndexBaseList:
        try:
            opt_params = {
                "offset": (page - 1) * limit,
                "limit": limit
            }
            
            if _type == models.TmeIndexType.GROUP:
                opt_params["filter"] = models.TmeIndexType.GROUP
            elif _type == models.TmeIndexType.CHANNEL:
                opt_params["filter"] = models.TmeIndexType.CHANNEL
            elif _type == models.TmeIndexType.BOT:
                opt_params["filter"] = models.TmeIndexType.BOT
            
            search_res = self.meilisearch.index.search(keywords, opt_params=opt_params)
        except Exception as e:
            logger.error(f"搜索引擎发生错误: {e}")
            raise Exception("搜索引擎发生错误")
        
        try:
            index_schemas = []
            for search_item in search_res:
                index_schema = schemas.TmeIndexBase.model_validate(search_item)
                index_schemas.append(index_schema)
        except Exception as e:
            logger.error(f"搜索结果序列化发生错误: {e}")
            raise Exception("搜索结果序列化发生错误")
        
        return schemas.TmeIndexBaseList(
            page=page,
            limit=limit,
            next=True if len(search_res) >= limit else False,
            list=index_schemas,
        )
