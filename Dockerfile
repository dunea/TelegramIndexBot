# 使用 Python 3.12 官方镜像作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /work

# 复制项目文件到工作目录
COPY . /work

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口（如果你的应用需要监听端口）
EXPOSE 8000

# 设置容器启动时要执行的命令
CMD ["python", "cmd/runserver/main.py"]