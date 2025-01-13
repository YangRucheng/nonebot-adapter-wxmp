# ---- 构建阶段 ----
FROM docker.proxy.yangrucheng.top/python:3.12-alpine AS builder

# 安装必要的构建工具和依赖
RUN sed -i 's#https\?://dl-cdn.alpinelinux.org/alpine#https://mirrors.tuna.tsinghua.edu.cn/alpine#g' /etc/apk/repositories \
    && apk add --no-cache gcc musl-dev libffi-dev sqlite-dev tzdata

# 安装依赖
COPY ./requirements.txt /app/requirements.txt
RUN pip config set global.index-url https://pypi.proxy.yangrucheng.top/simple \
    && pip config set global.trusted-host pypi.proxy.yangrucheng.top \
    && pip install --upgrade pip --break-system-packages \
    && pip install -r /app/requirements.txt --break-system-packages

# ---- 生产阶段 ----
FROM docker.proxy.yangrucheng.top/python:3.12-alpine

# 安装基础依赖
RUN apk add --no-cache \
    tzdata

# 设置时区
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo Asia/Shanghai > /etc/timezone

# 设置工作目录和数据卷
WORKDIR /app

# 从构建阶段复制已安装的 Python 包
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# 复制应用代码
COPY . /app

# 设置启动命令
CMD ["python3", "bot.py"]