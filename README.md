# TelegramIndexBot

## Alembic 迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "init"
# 执行迁移
alembic upgrade head
# 回滚迁移
alembic downgrade
```

## 开发常用命令

```bash
# 运行api
uvicorn main:app --reload

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/Scripts/activate

# linux 激活虚拟环境
source .venv/bin/activate

# 退出虚拟环境
deactivate

# 导出依赖
pip freeze > requirements.txt

# 安装依赖
pip install -r requirements.txt

# 运行
python ./cmd/runserver/main.py

# linux虚拟环境运行
nohup python3 ./cmd/runserver/main.py > ./run.log 2>&1 & echo $! > ./run.pid

# linux查看日志
less ./run.log

# linux查看日志末尾实时日志
tail ./run.log

# linux查看run.pid是否在运行
pid=$(cat run.pid)
ps -p $pid

# 读取 run.pid 文件获取进程 ID 杀死进程
pid=$(cat run.pid)
kill $pid
kill -9 $pid

# linux更新git版本
git stash
git pull
git stash pop
```