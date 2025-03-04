import copy
import re
from datetime import datetime, timezone, timedelta
from typing import Optional, Mapping, Any, cast, Union, Dict, List

from injector import inject
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, scoped_session

from app import models, schemas
from app.core.logger import logger
from app.core.meilisearch import MeiliSearch
from app.core.tme_scraper import TmeScraper


class QueryDataService:
    @inject
    def __init__(self, session: scoped_session[Session]):
        self.session = session
    
    def set_query_parameter(self, parameter: Union[Dict, List]) -> models.QueryData:
        with self.session() as session:
            try:
                data = models.QueryData(parameter=parameter)
                session.add(data)
                session.commit()
                session.refresh(data)
                
                # **深拷贝对象，防止 session 关闭后仍然引用 ORM**
                detached_data = copy.deepcopy(data)
                
                return detached_data
            except SQLAlchemyError as e:
                session.rollback()
                raise Exception("设置查询参数失败") from e
            except Exception as e:
                session.rollback()
                raise Exception("设置查询参数失败") from e
    
    def set_query_parameters(self, parameters: list[Union[Dict, List]]) -> list[models.QueryData]:
        with self.session() as session:
            try:
                datas = [models.QueryData(parameter=parameter) for parameter in parameters]
                session.bulk_save_objects(datas)
                session.commit()
                
                # 刷新每个对象以获取数据库生成的值（如 ID）
                for data in datas:
                    session.refresh(data)
                
                # **深拷贝对象，防止 session 关闭后仍然引用 ORM**
                detached_datas = copy.deepcopy(datas)
                
                return detached_datas
            except SQLAlchemyError as e:
                session.rollback()
                raise Exception("设置查询参数列表失败") from e
            except Exception as e:
                session.rollback()
                raise Exception("设置查询参数列表失败") from e
    
    def update_query_parameter(self, _id: str, parameter: Union[Dict, List]) -> models.QueryData:
        with self.session() as session:
            try:
                data = session.query(models.QueryData).filter(models.QueryData.id == _id).update(
                    {models.QueryData.parameter: parameter})
                session.commit()
                session.refresh(data)
            except SQLAlchemyError as e:
                session.rollback()
                raise Exception("更新参数失败") from e
            except Exception as e:
                session.rollback()
                raise Exception("更新参数失败") from e
            
            # **深拷贝对象，防止 session 关闭后仍然引用 ORM**
            detached_data = copy.deepcopy(data)
            
            return cast(models.QueryData, detached_data)
    
    def get_query_parameter(self, _id: str) -> models.QueryData:
        with self.session() as session:
            try:
                data: Optional[models.QueryData] = session.query(models.QueryData).filter(
                    models.QueryData.id == _id).one_or_none()
            except SQLAlchemyError as e:
                session.rollback()
                raise Exception("查询参数失败") from e
            except Exception as e:
                session.rollback()
                raise Exception("查询参数失败") from e
            
            if data is None:
                raise Exception("查询参数不存在或已过期")
            
            # **深拷贝对象，防止 session 关闭后仍然引用 ORM**
            detached_data = copy.deepcopy(data)
            
            return detached_data
    
    def get_query_parameters(self, _ids: list[str]) -> list[models.QueryData]:
        with self.session() as session:
            try:
                parameters = session.query(models.QueryData).filter(models.QueryData.id.in_(_ids)).all()
            except SQLAlchemyError as e:
                session.rollback()
                raise Exception("查询参数列表失败") from e
            except Exception as e:
                session.rollback()
                raise Exception("查询参数列表失败") from e
            
            # **深拷贝对象，防止 session 关闭后仍然引用 ORM**
            detached_parameters = copy.deepcopy(parameters)
            
            return cast(list[models.QueryData], detached_parameters)
