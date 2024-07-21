from langchain.agents import load_tools

# Load the tools with the specified parameters directly specified for each tool
loaded_tools = load_tools(
    tool_names=["awslambda", "awslambda", "awslambda"],
    awslambda_tool_name="Email Sender",
    awslambda_tool_description="Sends an email with specified content",
    function_name="sendEmailFunction",  # Adjust parameter names if needed
    awslambda_tool_name2="Data Logger",
    awslambda_tool_description2="Logs data entries to a specified database",
    function_name2="logDataFunction",  # Adjust parameter names if needed
    awslambda_tool_name3="Data Processor",
    awslambda_tool_description3="Processes data according to specified rules",
    function_name3="processDataFunction"  # Adjust parameter names if needed
)

# Now `loaded_tools` will contain the instances of each AWS Lambda tool
for tool in loaded_tools:
    print(f"Loaded tool: {tool.name} - {tool.description}")
