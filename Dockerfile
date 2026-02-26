# 基于官方 Python 3.13.5 (Debian 11)
FROM xuetangx-registry.cn-beijing.cr.aliyuncs.com/xc-project/mirrors/docker.io/library/python:3.13.5-bullseye

LABEL maintainer="hanyujian"
LABEL description="Python 3.13.5 + Playwright UI (Debian 11)"

# 设置工作目录
WORKDIR /root/PlaywrightUI

# 使用阿里云 Debian 源，加速 apt
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com\/debian-security/g' /etc/apt/sources.list && \
    apt update && \
    apt install -y --no-install-recommends \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 使用阿里云 pip 源
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
    && pip config set install.trusted-host mirrors.aliyun.com

# 复制项目文件
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright 的chromium浏览器和依赖
RUN playwright install-deps chromium && playwright install chromium 