import re
import requests
from bs4 import BeautifulSoup
import urllib3

import functools
import time
from termcolor import colored
import yaml

def retry(max_retries=3, retry_delay=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"发生异常：{e}")
                    if i < max_retries - 1:
                        print(f"等待 {retry_delay} 秒后重试...")
                        time.sleep(retry_delay)
                    else:
                        print("所有重试失败")
                        raise
        return wrapper
    return decorator

#大改
def cat_html(url: str) -> str:
    # 去掉引号和两端的空白字符
    url = re.sub(r'^["\']|["\']$', '', url).strip()
    
    # 禁用 InsecureRequestWarning
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # 获取 HTML 内容
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers, verify=False)  # 添加自定义用户代理和禁用 SSL 验证
    
    response.raise_for_status()  # 确保请求成功
    
    # 解析 HTML
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 提取页面上的所有文本内容
    body_content = soup.find('body')
    if body_content:
        text_content = body_content.get_text(separator="\n", strip=True)
    else:
        text_content = "No body content found"
    # text_content = filter_html_content(text_content)
    return text_content

def filter_html_content(html_content: str) -> str:
    #调用openai进行过滤
    import openai
    from openai import OpenAI
    OPENAI_API_KEY="fk226045-86bE8m1xlyX1DhsqAZc2JtvGVJlCjcvi"
    OPENAI_API_BASE="https://oa.api2d.net"
    client = OpenAI(api_key=OPENAI_API_KEY,base_url=OPENAI_API_BASE)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "过滤掉html标签,只保留漏洞利用的相关内容"+html_content}]
    )
    return response.choices[0].message.content

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as config_stream:
        return yaml.safe_load(config_stream)

def print_AutoRT():
    ascii_art = """
     _              _             ____    _____ 
    / \     _   _  | |_    ___   |  _ \  |_   _|
   / _ \   | | | | | __|  / _ \  | |_) |   | |  
  / ___ \  | |_| | | |_  | (_) | |  __/    | |  
 /_/   \_\  \__,_|  \__|  \___/  |_|       |_|  
    """
    color = 'red'  # Set the color to red

    for line in ascii_art.splitlines():
        print(colored(line, color))