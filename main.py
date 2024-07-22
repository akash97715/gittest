tool1 = LambdaTool.create(
    function_name="arn:aws:lambda::function:sbx-vox-agent-tool-example",
    region="us-east-1",
    tool_name="awslambda",
    tool_description="Sends an email with specified content"
)

tools = [tool1]
