from langchain.agents import load_tools

# Load each AWS Lambda tool separately to ensure unique configurations
tool1 = load_tools(
    tool_names=["awslambda"],
    awslambda_tool_name="Email Sender",
    awslambda_tool_description="Sends an email with specified content",
    function_name="sendEmailFunction"
)

tool2 = load_tools(
    tool_names=["awslambda"],
    awslambda_tool_name="Data Logger",
    awslambda_tool_description="Logs data entries to a specified database",
    function_name="logDataFunction"
)

tool3 = load_tools(
    tool_names=["awslambda"],
    awslambda_tool_name="Data Processor",
    awslambda_tool_description="Processes data according to specified rules",
    function_name="processDataFunction"
)

# Now `tool1`, `tool2`, and `tool3` contain the instances of each AWS Lambda tool
for tools in [tool1, tool2, tool3]:
    for tool in tools:
        print(f"Loaded tool: {tool.name} - {tool.description}")
