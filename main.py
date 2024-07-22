import operator
from typing import Annotated, List, TypedDict, Union

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage
from langchain.prebuilt.tool_executor import ToolExecutor
from langgraph.graph import END, StateGraph, START

class AgentState(TypedDict):
    input: str
    chat_history: List[BaseMessage]
    agent_outcome: Union[AgentAction, AgentFinish, None]
    intermediate_steps: Annotated[List[tuple[AgentAction, str]], operator.add]

class WorkflowManager:
    def __init__(self, config):
        self.config = config
        self.tool_executor = ToolExecutor(self.config['tools'])
        self.workflow = self.setup_workflow()

    def setup_workflow(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", self.run_agent)
        workflow.add_node("action", self.execute_tools)
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "continue": "action",
                "end": END,
            }
        )
        workflow.add_edge("action", "agent")
        return workflow.compile()

    def run_agent(self, data):
        agent_outcome = self.config['agent_runnable'].invoke(data)
        return {"agent_outcome": agent_outcome}

    def execute_tools(self, data):
        agent_action = data["agent_outcome"]
        output = self.tool_executor.invoke(agent_action)
        return {"intermediate_steps": [(agent_action, str(output))]}

    def should_continue(self, data):
        if isinstance(data["agent_outcome"], AgentFinish):
            return "end"
        else:
            return "continue"

    def run(self, query):
        inputs = {"input": query, "chat_history": []}
        return self.workflow.invoke(inputs)

# Example usage:
config = {
    'tools': [],  # Replace with actual tools configuration
    'agent_runnable': lambda data: AgentAction()  # Replace with actual runnable logic
}
manager = WorkflowManager(config)
result = manager.run("get the weather in India and then send an email. Use Lambda email tool")
