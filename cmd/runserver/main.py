import asyncio
import os
import sys
import time

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import multiprocessing

# 获取 main.py 所在目录
current_file_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（即 app 和 cmd 的父目录）
project_root = os.path.dirname(os.path.dirname(current_file_dir))
# 将项目根目录添加到 sys.path
sys.path.insert(0, project_root)

from app.core.settings import settings
from app.api.middlewares.exception import exception_handler
from app.api.v1 import index_route
from app.bot import Bot


def run_api():
    app = FastAPI()
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有来源
        allow_credentials=True,
        allow_methods=["*"],  # 允许所有HTTP方法
        allow_headers=["*"],  # 允许所有HTTP头
    )
    
    # 注册异常处理器
    app.add_exception_handler(Exception, exception_handler)
    
    # 将路由注册到应用中
    app.include_router(index_route, prefix="/api/v1/index")
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, timeout_keep_alive=60, timeout_notify=60)
    server = uvicorn.Server(config)
    asyncio.run(server.serve())


def run_bot():
    Bot(settings.BOT_TOKEN).run_polling()


if __name__ == '__main__':
    # 创建进程对象
    p_run_api = multiprocessing.Process(target=run_api)
    p_run_bot = multiprocessing.Process(target=run_bot)
    
    # 启动进程
    p_run_api.start()
    p_run_bot.start()
    
    # 等待进程结束
    try:
        while p_run_api.is_alive() and p_run_bot.is_alive():
            time.sleep(0.1)
        
        # 若有一个进程结束，终止另一个进程
        if p_run_api.is_alive():
            p_run_api.terminate()
            p_run_api.join()
        if p_run_bot.is_alive():
            p_run_bot.terminate()
            p_run_bot.join()
    except KeyboardInterrupt:
        # 若用户手动中断，终止所有进程
        p_run_api.terminate()
        p_run_bot.terminate()
        p_run_api.join()
        p_run_bot.join()
