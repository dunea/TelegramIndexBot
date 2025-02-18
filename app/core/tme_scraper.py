from typing import Any, Literal, Optional, TypeAlias
from bs4 import BeautifulSoup
import requests
from pydantic import BaseModel


class ScraperResult(BaseModel):
    content: str
    headers: dict[str, Any]
    cookies: list[dict[str, Any]]
    status_code: int
    task_id: str
    created_at: str
    updated_at: str


class ScraperResults(BaseModel):
    results: list[ScraperResult]


# 定义 Literal 类型别名
TmeType: TypeAlias = Literal["group", "channel", "bot", "user", "invalid"]


class TmeInfo(BaseModel):
    type: TmeType
    nickname: Optional[str] = None
    description: Optional[str] = None
    count_members: Optional[int] = None


class TmeScraper:
    def __init__(self, token: str):
        self.token = token
    
    def _get_html(self, username: str) -> ScraperResults:
        url = "https://scraper-api.smartproxy.com/v2/scrape"
        
        payload = {
            "url": f"https://t.me/{username}",
            "successful_status_codes": [200]
        }
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {self.token}"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        return ScraperResults.model_validate(response.json())
    
    def get_tme_info(self, username: str) -> TmeInfo:
        html_res = self._get_html(username)
        type_and_members = self._get_type_members(html_res.results[0].content)
        nickname_and_desc = self._get_nickname_description(html_res.results[0].content)
        return TmeInfo(
            type=type_and_members[0],
            nickname=nickname_and_desc[0],
            description=nickname_and_desc[1],
            count_members=type_and_members[1],
        )
    
    @staticmethod
    def _get_type_members(html: str) -> tuple[TmeType, int | None]:
        chat_type: Optional[TmeType] = None
        chat_member_num: Optional[int] = None
        
        # 创建 BeautifulSoup 对象
        soup = BeautifulSoup(html, "lxml")
        
        # 获取第一个 body 标签
        first_body = soup.find("body")
        if not first_body:
            raise Exception("没有找到Telegram响应信息")
        
        first_body_str = str(first_body)
        
        # 查找所有 tgme_page_extra 类的 div 标签
        target_divs = first_body.find_all('div', recursive=True, class_='tgme_page_extra')
        
        # 遍历每个 div 标签进行判断
        for target_div in target_divs:
            text = target_div.get_text(strip=True)  # 去除首尾空格
            
            # bot
            if '>Start Bot</a>' in first_body_str:
                chat_type = "bot"
                if "monthly users" in text:
                    extra = text.replace("monthly users", "").replace(" ", "")  # 确保赋值
                    try:
                        chat_member_num = int(extra)
                    except ValueError:
                        pass
            # channel
            elif 'subscribers' in text:
                chat_type = "channel"
                extra = text.replace("subscribers", "").replace(" ", "")  # 确保赋值
                try:
                    chat_member_num = int(extra)
                except ValueError:
                    pass
            # group
            elif "members" in text and '>View in Telegram</a>' in first_body_str:
                chat_type = "group"
                
                # 判断extra是否有逗号，若有，则取逗号前的数字
                if "," in text:
                    extra = text.split(",")[0]
                else:
                    extra = text
                extra = extra.replace("members", "").replace(" ", "")  # 确保赋值
                try:
                    chat_member_num = int(extra)
                except ValueError:
                    pass
            
            # 如果已经找到了类型和人数，可以提前退出
            if chat_type and chat_member_num is not None:
                break
        
        if chat_type is None:
            # invalid
            if "<div class=\"tgme_page_icon\">" in first_body_str:
                chat_type = "invalid"
            # user
            elif '>Send Message</a>' in first_body_str:
                chat_type = "user"
        
        if chat_type is None:
            raise Exception("未找到符合条件的Telegram信息")
        
        return chat_type, chat_member_num
    
    @staticmethod
    def _get_nickname_description(html: str) -> tuple[str, str | None]:
        description: Optional[str] = None
        
        # 创建 BeautifulSoup 对象
        soup = BeautifulSoup(html, "lxml")
        
        # 获取第一个 head 标签
        first_head = soup.find("head")
        
        # 获取nickname
        meta_tag = first_head.find("meta", property="og:title")
        if meta_tag:
            nickname = meta_tag.get('content')
        else:
            raise Exception("获取Telegram昵称发生错误")
        
        # 获取description
        meta_tag = first_head.find("meta", property="og:description")
        if meta_tag:
            description = meta_tag.get('content')
        
        return nickname, description
