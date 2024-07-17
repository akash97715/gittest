pip install datamodel-code-generator


datamodel-codegen --input parser.json --input-file-type json --output models.py


from pydantic import BaseModel, ValidationError, create_model
from typing import Any, Dict, Type
import json

class LambdaWrapper:
    lambda_client: Any
    function_name: str

    def __init__(self, lambda_client: Any, function_name: str):
        self.lambda_client = lambda_client
        self.function_name = function_name

    def generate_and_validate_model(self, json_data: Dict) -> Dict:
        """
        Dynamically generates a Pydantic model from the JSON schema and validates the JSON data.
        """
        # Assuming json_data is a dictionary representing the payload
        fields = {key: (type(value), ...) for key, value in json_data.items()}
        DynamicModel = create_model('DynamicModel', **fields)

        try:
            # Validate the data using the dynamically generated model
            model_instance = DynamicModel(**json_data)
            print("Validation successful:", model_instance)
            return {"status": "success", "data": model_instance.dict()}
        except ValidationError as e:
            print("Validation failed:", e)
            return {"status": "error", "message": str(e)}

    def run(self, state: Dict) -> Dict:
        """
        Main execution method that uses the dynamic model generation.
        """
        # Validate the input JSON using a dynamically generated model
        result = self.generate_and_validate_model(state)
        return result

# Usage example
lambda_client = None  # Placeholder for the actual AWS Lambda client
wrapper = LambdaWrapper(lambda_client, 'example_function')
incoming_json = {'name': 'John Doe', 'age': 30}
result = wrapper.run(incoming_json)
