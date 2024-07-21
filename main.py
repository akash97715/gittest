from langchain.agents import load_tools

# Define the parameters for each AWS Lambda tool
lambda_tools_parameters = {
    "awslambda_tool_name1": "Email Sender",
    "awslambda_tool_description1": "Sends an email with specified content",
    "awslambda_function_name1": "sendEmailFunction",

    "awslambda_tool_name2": "Data Logger",
    "awslambda_tool_description2": "Logs data entries to a specified database",
    "awslambda_function_name2": "logDataFunction",

    "awslambda_tool_name3": "Data Processor",
    "awslambda_tool_description3": "Processes data according to specified rules",
    "awslambda_function_name3": "processDataFunction"
}

# Load the tools with the specified parameters
loaded_tools = load_tools(
    tool_names=["awslambda", "awslambda", "awslambda"],
    **lambda_tools_parameters
)

# Now `loaded_tools` will contain the instances of each AWS Lambda tool
for tool in loaded_tools:
    print(f"Loaded tool: {tool.name} - {tool.description}")
