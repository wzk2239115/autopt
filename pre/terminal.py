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
        if command.startswith("python" or "python3"):
            # self.timeout = 60*20 # 20 minutes for python scripts
            command = "echo '[+] Current token is q5yPj8NeMYow8xxBPREjSytwS2cICv84xJ53ekrIDVE'"
        if 'nano ' in command:
            command = "echo 'nano is not supported in this environment'"
            
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

if __name__ == '__main__':
    # DEMO
    with InteractiveShell() as shell:
        print("="*60)
        print(shell.execute_command('curl -I "http://172.19.0.1:8080"'))

