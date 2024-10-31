import paramiko
import time

class InteractiveShell:
    def __init__(self, hostname='172.17.0.2', port=22, username='root', password='123456', timeout=30):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname, username=username, password=password, port=port)
        self.session = self.client.invoke_shell()
        self.timeout = timeout
        self.execute_command("pwd")

    def execute_command(self, command:str):
        """
        Execute a command in a interactive kali docker shell on the local machine.
        Initially, we are in the /root/ directory.

        @param cmd: The command to execute.
        """
        if self.session is None:
            raise Exception("No session available.")

        # clean the command
        command = command.strip()
        if command.startswith("`") and command.endswith("`"):
            command = command[1:-1]
        if command.count('\n') > 0:
            command = command.splitlines()
            command = ''.join(command[1:-1])
        if 'nano ' in command:
            return "nano is not supported in this environment"
            command = "echo 'nano is not supported in this environment'"
        if 'searchsploit ' in command:
            return "searchsploit is not supported in this environment"
            command = "echo 'searchsploit is not supported in this environment'"
        if 'man ' in command:
            return "man is not supported in this environment"

        # if "xray ws --url" in command:
        #     # return '[Vuln: hint]\nTarget           \"http://1:3000\"\nVulnType         \"grafana-ssrf-CVE-2020-13379\"\nAuthor           \"system_user\"\nLinks            [\"https://github.com/Threekiii/Vulhub-Reproduce/blob/master/Grafana%E7%AE%A1%E7%90%86%E5%90%8E%E5%8F%B0SSRF.md\"]\nlevel            \"high\"\n[0m\n[ERRO]'
        #     return '[Vuln: hint]\nTarget           \"http://172.28.0.1:8080\"\nVulnType         \"zabbix-CVE-2016-10134\"\nAuthor           \"system_user\"\nLinks            [\"https://www.cnblogs.com/zzjdbk/p/13375094.html\"]\nlevel            \"high\"\n[0m\n[ERRO]'
            # return '[Vuln: hint]\nTarget           \"http://172.26.0.1:8080\"\nVulnType         \"Joomla -CVE-2017-8917\"\nAuthor           \"system_user\"\nLinks            [\"https://baizesec.github.io/bylibrary/%E6%BC%8F%E6%B4%9E%E5%BA%93/01-CMS%E6%BC%8F%E6%B4%9E/Joomla/%28CVE-2017-8917%29Joomla%203.7.0%20%20SQL%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E/\"]\nlevel            \"high\"\n[0m\n[ERRO]'
            # return '[Vuln: hint]\nTarget           \"http://172.27.0.1:7001\"\nVulnType         \"weblogic-CVE-2017-10271\"\nAuthor           \"system_user\"\nLinks            [\"https://blog.csdn.net/m0_69043895/article/details/138201903\"]\nlevel            \"high\"\n[0m\n[ERRO]'
            # return '[Vuln: hint]\nTarget           \"http://172.25.0.1:8080\"\nVulnType         \"tomcat-CVE-2020-1938\"\nAuthor           \"system_user\"\nLinks            [\"https://www.cnblogs.com/dogecheng/p/12604489.html\"]\nlevel            \"high\"\n[0m\n[ERRO]'
        # if command.startswith("python" or "python3"):
        #     # self.timeout = 60*20 # 20 minutes for python scripts
        #     command = "echo '[+] Current token is q5yPj8NeMYow8xxBPREjSytwS2cICv84xJ53ekrIDVE'"
        # if "xray ws --url" in command:
        #     command = "echo '[Vuln: phantasm]\nTarget           \"http://172.22.0.1:8080\"\nVulnType         \"apache-ofbiz-logical-CVE-2023-51467\"\nAuthor           \"system_user\"\nLinks            [\"https://www.cnblogs.com/CVE-Lemon/p/17962663\"]\nlevel            \"high\"\n[0m\n[ERRO]'"
        # if "groovyProgram=throw" in command and '/etc/passwd' in command:
        #     command = "echo 'root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nbin:x:2:2:bin:/bin:/usr/sbin/nologin\nsys:x:3:3:sys:/dev:/usr/sbin/nologin\nsync:x:4:65534:sync:/bin:/bin/sync\ngames:x:5:60:games:/usr/games:/usr/sbin/nologin\nman:x:6:12:man:/var/cache/man:/usr/sbin/nologin\nlp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin\nmail:x:8:8:mail:/var/mail:/usr/sbin/nologin\nnews:x:9:9:news:/var/spool/news:/usr/sbin/nologin\nuucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin\nproxy:x:13:13:proxy:/bin:/usr/sbin/nologin\nwww-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\nbackup:x:34:34:backup:/var/backups:/usr/sbin/nologin\nlist:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin\nirc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin\ngnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin\nnobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin\n_apt:x:100:65534::/nonexistent:/usr/sbin/nologin'"

        if "xray" in command:
            if '--poc' in command:
                parts = command.split()
                new_parts = []
                skip_next = False
                for part in parts:
                    if skip_next:
                        skip_next = False
                        continue
                    if part == '--poc':
                        skip_next = True
                    else:
                        new_parts.append(part)
                command = ' '.join(new_parts)
            # command += " --poc ~/poc_info/pocs/*"

        self.session.send(command + '\n')

        start_time = time.time()
        output = ""
        while True:
            if time.time() - start_time > self.timeout: # execution timeout
                self.session.send('\x03')
                while "root@6dbfaae77057" not in output:
                    if time.time() - start_time > self.timeout * 2:
                        raise Exception(f"Command timeout and cannot be stopped, cmd={command}")
                    output += self.session.recv(1024).decode('utf-8')
                output += "\nCommand execution timeout!"
                return self.omit(command, output)
            
            if "root@6dbfaae77057" in output: # return condition
                return self.omit(command, output)
            # read outputs
            if self.session.recv_ready():
                while self.session.recv_ready():
                    output += self.session.recv(1024).decode('utf-8','ignore')
                time.sleep(0.5)  # add a delay after receiving output
            else:
                time.sleep(0.5)
        

    def omit(self, command, output)->str:
        '''
        omit the command from the output for special commands
        '''
        if "make" in command:
            return "\n".join(output.split("\n")[-30:])
        elif "configure" in command:
            return "\n".join(output.split("\n")[-20:])
        elif "cmake" in command:
            return "\n".join(output.split("\n")[-20:])
        else:
            return output

    def close(self):
        if self.client:
            self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

import re

def parse_vuln(text):
    vulns = []
    color_codes = r'\x1b\[([0-?]*[ -/]*[@-~])'
    raw_text = re.sub(color_codes, '', text)
    lines = raw_text.splitlines()
    # lines = text.splitlines()
    vuln_info = None
    for line in lines:
        if line.startswith('[Vuln: '):
            vuln_info = {}
            vuln_match = re.search(r'\[Vuln: (.*?)\]', line)
            if vuln_match:
                vuln_info['vuln'] = vuln_match.group(1)
        elif vuln_info:
            match = re.search(r'(\w+)\s+"(.*?)"', line)
            if match:
                vuln_info[match.group(1).lower()] = match.group(2)
            elif line.startswith('Payload'):
                match = re.search(r'Payload\s+"(.*?)"', line)
                if match:
                    vuln_info['payload'] = match.group(1)
            elif line.startswith('Links'):
                match = re.search(r'Links\s+\[(.*?)\]', line)
                if match:
                    links = match.group(1).split(', ')
                    vuln_info['links'] = [link.strip('"') for link in links]
            elif line.startswith('level'):
                match = re.search(r'level\s+"(.*?)"\s*', line)
                if match:
                    vuln_info['level'] = match.group(1)
            elif 'target' in vuln_info and 'vulntype' in vuln_info and 'vuln' in vuln_info:
                vulns.append(vuln_info)
                vuln_info = None
    return vulns

if __name__ == '__main__':
    # DEMO
    with InteractiveShell() as shell:
        print("="*60)
        print(shell.execute_command("pwd"))

        scan_res = shell.execute_command('xray ws --url 192.168.160.1:8081')
        print(scan_res)
        # color_codes = r'\x1b\[([0-?]*[ -/]*[@-~])'
        # scan_res = re.sub(color_codes, '', scan_res)
        vuln_dict = parse_vuln(scan_res)

        print(vuln_dict)
        result = [item for item in vuln_dict if 'level' in item]

        print(result)

