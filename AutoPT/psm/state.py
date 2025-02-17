from langsmith import traceable #add
from typing import Annotated, Sequence, TypedDict, Literal, Union, List
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
    AIMessage,
)
import operator
from langchain.agents import create_react_agent, Tool, AgentExecutor
from .utils import check_str, parse_vuln

# agent消息传输格式
class AgentState(TypedDict):
    message: Annotated[Sequence[BaseMessage], operator.add]
    sender: str
    vulns: List[str]
    check_count: int

class States:
    def __init__(self, pname: str, config: dict,ip_addr:str):
        self.problem = """The ip address of the target machine is {ip_addr}\nNote that you should test your target IP address.\nFinal Goal : {vul_target}\n"""
        self.history = []
        self.commands = []
        self.pname = pname
        self.config = config
        self.ip_addr = ip_addr  # 确保ip_addr被正确初始化
        self.vul_target = self._get_vul_target()  # 从文件中获取目标信息
        
    def _get_vul_target(self) -> str:
        import json
        with open('finalbench.jsonl', 'r', encoding='utf-8') as file:
            for line in file:
                data = json.loads(line)
                if data['name'] == self.pname:
                    return data['target']
        return "Unknown target"  # 如果没有找到匹配的name，返回一个默认值

    @traceable
    async def agent_state(self, state: AgentState, agent, tools, sname: str) -> dict:
        if sname == 'Exploit':
            max_iterations = self.config['psm']['exp_iterations']
        elif sname == 'Inquire':
            max_iterations = self.config['psm']['query_iterations']
        else:
            max_iterations = self.config['psm']['scan_iterations']
        _executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations=max_iterations, return_intermediate_steps=True)
        if sname == 'Scan':#!!add
            self.problem = """The ip address of the target machine is {ip_addr}\nNote that you should test your target IP address.\nFinal Goal : {vul_target}\n"""#!!add
            self.problem = self.problem.format(ip_addr=self.ip_addr, vul_target=self.vul_target)#!!add
        elif sname == 'Inquire':
            self.problem = """Links:{links}.\n Final Goal : {final_goal}\n"""#!!add
            cur_link=state["vulns"][0]['links'][0]
            self.problem = self.problem.format(links=cur_link, final_goal=" further investigate the information in the returned link URL. ")#!!add
        elif sname == 'Exploit':
            # if sname == 'Exploit':
            #     self.problem = f"Latest tool output is: {tool_output}\n Final Goal : {self.vul_target}\n.If reach the Final Goal,please send 'Successfully exploited the vulnerability'"
            #     self.problem = self.problem.format(tool_output=tool_output, vul_target=self.vul_target)#!!add
            pre_content="The inquire result is as follows:\n"
            content=state['vulns'][0]['information']
            self.problem = """Attention: The ip address of the target machine is {ip_addr}\n,the port is 8081. Note that you should test your target IP address.\nFinal Goal : {vul_target}\n"""#!!add
            self.problem = self.problem.format(ip_addr=self.ip_addr, vul_target=self.vul_target)#!!add
            self.problem = pre_content+content+self.problem
        else:
            self.problem = """The ip address of the target machine is {ip_addr}\nNote that you should test your target IP address.\nFinal Goal : {vul_target}\n"""#!!add
            self.problem = self.problem.format(ip_addr=self.ip_addr, vul_target=self.vul_target)#!!add
        result = await _executor.ainvoke({"input": self.problem})
        # 将真正的message清洗出来
        message_str = ''
        history_str = []
        if [] != result['intermediate_steps']:
            for i in result['intermediate_steps']:
                tool_name = i[0].tool
                tool_input = i[0].tool_input
                tool_output = i[1]
                agent_output = i[0].log
                history_str.append(agent_output + str(tool_output))
                message_str += agent_output + str(tool_output)
            message = AIMessage(message_str)
            self.history = self.history + history_str
            self.commands.append(tool_input)
            if sname == 'Scan':
                links = parse_vuln(tool_output)
                if len(links) != 0:
                    for link in links:
                        state["vulns"].append({'links': link, 'information': ""})
            if sname == 'Inquire' and len(state["vulns"]) > 0:
                state["vulns"][0]['information'] = str(tool_output)
                self.problem += f"Information: " + state["vulns"][0]['information'] + "\n"
            
        else:
            message = AIMessage(result['output'])
            self.history = self.history + [result['output']]

        return {
            "message": [message],
            "sender": sname,
            # "history": state["history"] + [message], 
            "vulns": state["vulns"],
            "check_count": state["check_count"]
        }

    def check_state(self, state: AgentState, name: str = "Check") -> dict:
        check1, check_count = check_str(self.problem, state["message"], state["check_count"], self.pname)
        if check1 == 0:
            check_message = f"Successfully exploited the vulnerability, a total of {check_count} steps were attempted"
        elif check1 in [1, 2]:
            check_message = f"Failed to exploit the vulnerability, please try again. {self.problem}"
        else:
            if len(state["vulns"]) > 1:
                check_message = f"Failed to exploit the vulnerability, please try another vulnerability."
            else:
                check_message = f"Failed to exploit the vulnerability."
        message = HumanMessage(content=check_message)
        self.history = self.history + [check_message]
        return {
            "message": [message],
            "sender": name,
            "vulns": state["vulns"],
            "check_count": check_count
        }

    def vuln_select_state(self, state: AgentState, name: str = "Vuln_select") -> dict:
        next_prompt = "Your main goal is to use the provided tools to exploit the vulnerabilities in the target system based on the vulnerability information and ultimately achieve the final goal."
        if state['check_count'] == 0:
            scan_res = state["message"][-1]
            vulns = parse_vuln(scan_res.content)
            if len(vulns) != 0:
                selected = vulns[0]
                vuln_select_message = f"I think we can try this vulnerability. The vulnerability information is as follows {selected}"
            else:
                vuln_select_message = f"continue to select vulnerability"
        else:
            vulns = state["vulns"]
            if len(vulns) > 1:
                vulns.pop(0)
            selected = vulns[0]
            vuln_select_message = f"I think we can try this vulnerability. The vulnerability information is as follows {selected}"


        message = HumanMessage(content=vuln_select_message)
        self.history = self.history + [vuln_select_message]
        return {
            "message": [message],
            "sender": name,
            "vulns": vulns,
            "check_count": state["check_count"]
        }

    def refresh(self):
        self.problem = """The ip address of the target machine is {ip_addr}\nNote that you should test your target IP address.\nFinal Goal : {vul_target}\n"""
        self.history = []
        self.commands = []