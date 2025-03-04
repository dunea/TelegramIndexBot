import copy
import re
from datetime import datetime, timezone, timedelta
from typing import Optional, Mapping, Any

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
    
    # 添加索引于详细信息
    def add_index_by_detail(self, detail: schemas.TmeIndexCreate) -> schemas.TmeIndexBase:
        with self.session() as session:
            # 查询
            try:
                index_ = session.query(models.TmeIndex).filter(
                    models.TmeIndex.username == detail.username).one_or_none()
            except Exception as e:
                logger.error(f"查询索引发生错误: {e}")
                raise Exception("查询索引发生错误")
            if index_ is not None:
                try:
                    index_schema = schemas.TmeIndexBase.model_validate(index_)
                except Exception as e:
                    logger.error(f"序列化索引发生错误: {e}")
                    raise Exception("序列化索引发生错误")
                
                try:
                    self.meilisearch.index.add_documents([index_schema.model_dump(mode='json')], primary_key="id")
                except Exception as e:
                    session.rollback()
                    logger.error(f"添加到搜索引擎发生错误: {e}")
                    raise Exception("添加到搜索引擎发生错误")
                
                return index_schema
            
            # 增加
            try:
                index = models.TmeIndex(
                    username=detail.username,
                    nickname=detail.nickname,
                    desc=detail.desc,
                    type=detail.type,
                    count_members=detail.count_members,
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
    
    # 添加索引于用户名
    def add_index_by_tme(self, username: str) -> schemas.TmeIndexBase:
        username = username.strip()
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
        tme_type = self._str_to_tme_index_type(tme_info.type)
        
        return self.add_index_by_detail(schemas.TmeIndexCreate(
            type=tme_type,
            username=username,
            nickname=tme_info.nickname,
            desc=tme_info.description,
            count_members=tme_info.count_members if tme_info.count_members is not None else 0,
        ))
    
    # 添加索引于链接
    def add_index_by_tme_link(self, tme_link: str) -> schemas.TmeIndexBase:
        # 正则获取tme_link
        username = self._re_get_tem_link_in_username_one(tme_link)
        
        # 添加
        return self.add_index_by_tme(username)
    
    # 添加索引链接于用户
    def add_index_tme_link_by_user(self, tme_link: str, chat_id: int) -> schemas.TmeIndexBase:
        # 正则获取tme_link
        username = self._re_get_tem_link_in_username_one(tme_link)
        
        # 添加索引于用户名
        tme_index = self.add_index_by_tme(username)
        
        # 添加到add_tme_index
        with self.session() as session:
            exist = session.query(models.UserAddIndex).filter(
                models.UserAddIndex.username == username,
                models.UserAddIndex.user_chat_id == chat_id,
            ).count()
            
            if exist <= 0:
                add_tme_index = models.UserAddIndex(
                    username=username,
                    user_chat_id=chat_id
                )
                session.add(add_tme_index)
                session.commit()
                session.refresh(add_tme_index)
        
        return tme_index
    
    # 删除索引于ID
    def del_index_by_id(self, _id: str) -> None:
        with self.session() as session:
            # 查询
            try:
                index_ = session.query(models.TmeIndex).filter(
                    models.TmeIndex.id == _id
                ).one_or_none()
            except Exception as e:
                logger.error(f"查询索引发生错误: {e}")
                raise Exception("查询索引发生错误")
            
            if index_ is None:
                logger.info(f"删除的索引不存在: {_id}")
                raise ValueError("删除的索引不存在")
            
            try:
                session.query(models.TmeIndex).filter(models.TmeIndex.id == _id).delete()
                session.commit()
            except Exception as e:
                logger.info(f"从数据库删除索引发生错误: {_id}")
                raise Exception("从数据库删除索引发生错误")
            
            try:
                self.meilisearch.index.delete_document(_id)
            except Exception as e:
                session.rollback()
                logger.error(f"从搜索引擎删除发生错误: {e}")
                raise Exception("从搜索引擎删除发生错误")
    
    # 删除索引根据username于用户
    def del_index_in_username_by_user(self, username: str, user_chat_id: int):
        with self.session() as session:
            # 查询
            try:
                index_ = session.query(models.UserAddIndex).filter(
                    models.UserAddIndex.username == username,
                    models.UserAddIndex.user_chat_id == user_chat_id,
                ).first()
            except Exception as e:
                logger.error(f"查询用户索引发生错误: {e}")
                raise Exception("查询用户索引发生错误")
            
            if index_ is None:
                logger.info(f"删除的用户索引不存在: {username}")
                raise ValueError("删除的用户索引不存在")
            
            try:
                session.query(models.UserAddIndex).filter(models.UserAddIndex.id == index_.id).delete()
                session.commit()
            except Exception as e:
                logger.info(f"删除用户索引发生错误: {index_.id}")
                raise Exception("删除用户索引发生错误")
    
    # 搜索索引
    def search_index(self, keywords: str, _type: models.TmeIndexType = None, page: int = 1,
                     limit: int = 20) -> schemas.TmeIndexBaseList:
        try:
            opt_params: dict[str, Any] = {
                "offset": (page - 1) * limit,
                "limit": limit
            }
            
            if _type == models.TmeIndexType.GROUP:
                opt_params["filter"] = f"type = {models.TmeIndexType.GROUP.value}"
            elif _type == models.TmeIndexType.CHANNEL:
                opt_params["filter"] = f"type = {models.TmeIndexType.CHANNEL.value}"
            elif _type == models.TmeIndexType.BOT:
                opt_params["filter"] = f"type = {models.TmeIndexType.BOT.value}"
            
            search_res = self.meilisearch.index.search(keywords, opt_params=opt_params)
            estimated_total_hits: int = search_res["estimatedTotalHits"]
        except Exception as e:
            logger.error(f"搜索引擎发生错误: {e}")
            raise Exception("搜索引擎发生错误")
        
        try:
            index_schemas = []
            for search_item in search_res["hits"]:
                index_schema = schemas.TmeIndexBase.model_validate(search_item)
                index_schemas.append(index_schema)
        except Exception as e:
            logger.error(f"搜索结果序列化发生错误: {e}")
            raise Exception("搜索结果序列化发生错误")
        
        return schemas.TmeIndexBaseList(
            total=estimated_total_hits,
            page=page,
            limit=limit,
            next=estimated_total_hits >= page * limit,
            list=index_schemas,
        )
    
    # 用户添加的索引
    def index_by_user_add(self, chat_id: int, page=1, limit=10) -> schemas.TmeIndexBaseList:
        with self.session() as session:
            try:
                add_index_list = session.query(models.UserAddIndex).filter(
                    models.UserAddIndex.user_chat_id == chat_id).order_by(
                    models.UserAddIndex.create_at).offset((page - 1) * limit).limit(limit).all()
            except:
                raise Exception("查询用户添加索引发生错误")
            
            add_index_usernames = []
            for add_index in add_index_list:
                add_index_usernames.append(add_index.username)
            
            try:
                index_list = session.query(models.TmeIndex).filter(
                    models.TmeIndex.username.in_(add_index_usernames)).all()
                index_schemas = []
                for index_item in index_list:
                    index_schema = schemas.TmeIndexBase.model_validate(index_item)
                    index_schemas.append(index_schema)
            except:
                raise Exception("查询索引信息发生错误")
        
        return schemas.TmeIndexBaseList(
            page=page,
            limit=limit,
            next=len(add_index_list) >= limit,
            list=index_schemas,
        )
    
    # 查询索引于id
    def query_index_by_id(self, _id: str) -> Optional[schemas.TmeIndexBase]:
        with self.session() as session:
            try:
                index = session.query(models.TmeIndex).filter(models.TmeIndex.id == _id).first()
            except:
                raise Exception("查询索引数据库发生错误")
            if index is None:
                return None
            
            return schemas.TmeIndexBase.model_validate(index)
    
    # 更新索引于id
    def update_index_by_id(self, _id: str, chat_id: int = None) -> Optional[schemas.TmeIndexBase]:
        with self.session() as session:
            # 从tme_index获取信息
            try:
                index = session.query(models.TmeIndex).filter(models.TmeIndex.id == _id).one_or_none()
            except:
                raise Exception("查询索引数据库发生错误")
            if index is None:
                return None
            
            # 判断今天是否更新了
            now = datetime.now(timezone.utc)
            six_hours_ago = now - timedelta(hours=6)
            
            if index.last_gather_at:
                last_gather_at_aware = index.last_gather_at.replace(tzinfo=timezone.utc)
                if six_hours_ago <= last_gather_at_aware <= now:
                    raise ValueError("每6小时仅能更新1次")
            
            tme_info = self.tme_scraper.get_tme_info(str(index.username))
            tme_type = self._str_to_tme_index_type(tme_info.type)
            
            # 更新数据到数据库
            try:
                session.query(models.TmeIndex).filter(models.TmeIndex.id == _id).update({
                    models.TmeIndex.nickname: tme_info.nickname,
                    models.TmeIndex.desc: tme_info.description,
                    models.TmeIndex.count_members: tme_info.count_members if tme_info.count_members is not None else 0,
                    models.TmeIndex.type: tme_type,
                    models.TmeIndex.last_gather_at: datetime.now(timezone.utc),
                })
                session.commit()
                session.refresh(index)
            except:
                raise Exception("更新信息到数据库发生错误")
            
            # 添加到meilisearch
            try:
                index_schema = schemas.TmeIndexBase.model_validate(index)
                self.meilisearch.index.add_documents([index_schema.model_dump(mode='json')], primary_key="id")
            except Exception as e:
                session.rollback()
                logger.error(f"添加到搜索引擎发生错误: {e}")
                raise Exception("添加到搜索引擎发生错误")
            
            return index_schema
    
    # 正则获取tme_link
    @staticmethod
    def _re_get_tem_link_in_username_one(tme_link: str) -> str:
        usernames = []
        pattern = r"https://t.me/([^/?')]{3,32})"
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
        
        return usernames[0]
    
    @staticmethod
    def _str_to_tme_index_type(type_str: str) -> models.TmeIndexType:
        if type_str == "invalid":
            raise ValueError("无法进行查询或不存在")
        elif type_str == "user":
            raise ValueError("暂不支持收录用户索引")
        elif type_str == "group":
            tme_type = models.TmeIndexType.GROUP
        elif type_str == "channel":
            tme_type = models.TmeIndexType.CHANNEL
        elif type_str == "bot":
            tme_type = models.TmeIndexType.BOT
        else:
            raise ValueError("不支持的收录类型")
        
        return tme_type
