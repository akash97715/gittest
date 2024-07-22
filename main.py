from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, Type, Union

# Assuming your LambdaTool and LambdaInput are defined as shown before

# Example usage, ensure data passed is correctly structured
tool1 = LambdaTool.create(
    function_name="arn:aws:lambda::function:sbx-vox-agent-tool-example",
    region="us-east-1",
    tool_name="awslambda",
    tool_description="Sends an email with specified content"
)

# Create an appropriate input
input_data = LambdaToolInput(data={"key": "value"})  # Correctly formatted as a dict

# Pass the data to the tool in a manner that matches the expected structure
# If using an AgentExecutor, ensure it is set up to handle this structure
agent_executor = AgentExecutor(agent=agent, tools=[tool1], verbose=True)

# Ensure the tool expects data in the correct format when called
agent_executor.invoke({"input": input_data.dict()})  # Here, ensure the structure passed is correct
