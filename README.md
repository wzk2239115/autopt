This anonymous library is set up for double-blind review. We will open source it after review.

## Legal and Ethical Statement

It is prohibited to use this project for any unauthorized penetration testing or any illegal activities. This project is only used for system security research.

## 使用方式

步骤一：启动kali和靶场
docker build -t kali . 构建kali

docker-compose up 启动kali

到对应的靶场文件夹里启动对应的靶场

步骤二：运行terminal.py看是否正确

python3 terminal.py

步骤三：

python3 main.py --name "thinkphp/5-rce" --ip_addr "taget_ip"

其中name填写对应finalbench.jsonl文件中的"name"

ip_addr对应靶场ip

