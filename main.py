    def _create_lambda_wrappers(self):
        for tool in self.config["tools"]:
            input_schema = tool.get("input_schema")  # Assuming input_schema is provided correctly
            output_schema = tool.get("output_schema")  # Assuming output_schema is provided correctly
            wrapper = LambdaWrapper.create(
                function_name=tool["arn"],
                tool_name=tool["name"],
                tool_description=f"Lambda function for {tool['name']}",
                region=tool["region"],
                input_schema=input_schema,
                output_schema=output_schema
            )
            self.lambda_wrappers[tool["name"]] = wrapper
