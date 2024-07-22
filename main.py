class LambdaWrapper(BaseModel):
    """Wrapper for AWS Lambda SDK."""
    lambda_client: Any  #: :meta private:
    function_name: str
    awslambda_tool_name: Optional[str] = None
    awslambda_tool_description: Optional[str] = None
    is_conditional_fn: bool = False
    
    @classmethod
    def create(cls, function_name: str, region: str):
        lambda_client = boto3.client("lambda", region_name=region)
        return cls(lambda_client=lambda_client, function_name=function_name)

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the specified AWS Lambda function with the given state as input."""
        response = self.lambda_client.invoke(
            FunctionName=self.function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps(state)  # Ensure 'state' is a dictionary
        )
        payload_stream = response['Payload']
        payload_string = payload_stream.read().decode("utf-8")
        response_data = json.loads(payload_string)
        
        if 'body' in response_data:
            return response_data['body']  # Return the 'body' part of the response if available

        return response_data  # Return the whole response otherwise
