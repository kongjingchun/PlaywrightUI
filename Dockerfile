FROM xuetangx-registry.cn-beijing.cr.aliyuncs.com/xc-project/xc/playwrightui:202603121022

# 工作目录
WORKDIR /root/PlaywrightUI

# 复制项目文件
COPY . .
