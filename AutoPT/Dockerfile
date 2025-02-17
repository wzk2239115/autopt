# 使用 Kali Linux 的滚动更新版本作为基础镜像
FROM kalilinux/kali-rolling:latest

# 设置环境变量，避免交互式提示
ENV DEBIAN_FRONTEND=noninteractive

# 更新包列表并安装一些常用的工具
RUN apt-get update && apt-get install -y \
    # kali-linux-large \
    net-tools \
    curl \
    vim \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装额外的工具（例如 nmap）
RUN apt-get update && apt-get install -y nmap \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装并配置SSH服务
RUN apt-get update && apt-get install -y openssh-server \
    && mkdir -p /var/run/sshd \
    && echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config \
    && echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config \
    && echo 'Port 2222' >> /etc/ssh/sshd_config \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置root密码为123456
RUN echo 'root:123456' | chpasswd

# 暴露SSH端口
EXPOSE 22

# 设置默认的命令行工具
CMD ["/bin/bash"]

# 安装xray
RUN apt-get update && apt-get install -y wget unzip \
    && wget https://github.com/chaitin/xray/releases/download/1.9.11/xray_linux_amd64.zip \
    && unzip xray_linux_amd64.zip -d /usr/local/bin/ \
    && mv /usr/local/bin/xray_linux_amd64 /usr/local/bin/xray \
    && chmod +x /usr/local/bin/xray \
    && cd /usr/local/bin/ \
    && xray version

# # 复制配置文件到用户目录
# RUN cp /usr/local/bin/module.xray.yaml /root/ \
#     && cp /usr/local/bin/plugin.xray.yaml /root/

# 设置工作目录
WORKDIR /usr/local/bin/
