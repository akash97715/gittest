# Assuming you have defined your tool and the input schema as follows:

class LambdaToolInput(BaseModel):
    """Input schema for the Lambda tool."""
    data: Dict[str, Any] = Field(default_factory=dict, description="Payload to send to the Lambda function.")

# Example usage of LambdaTool
tool1 = LambdaTool.create(
    function_name="arn:aws:lambda::function:sbx-vox-agent-tool-example",
    region="us-east-1",
    tool_name="awslambda",
    tool_description="Sends an email with specified content"
)

# This tool is added to the list of tools managed by the AgentExecutor
tools = [tool1]
agent = SomeAgentImplementation()  # Ensure you have an agent defined
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Correct formatting of the input to match what LambdaToolInput expects:
input_dict = {"input": json.dumps({"data": {"question": "what is LangChain?"}})}

# Now, invoke the executor with the correctly formatted input
try:
    response = agent_executor.invoke(input_dict)
    print(response)
except Exception as e:
    print(f"Error during invocation: {str(e)}")
