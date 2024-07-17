{
    "name": "Dummy Agent",
    "description": "This agent serves to demonstrate the workflow.",
    "prompt": "What is the meaning of life?",
    "system_prompt": "Assume that you are a philosopher influenced by Socrates.",
    "tools": [
        {
            "name": "retriever_tool",
            "arn": "lambda-arn-for-retriever",
            "region": "us-east-1",
            "input_schema": {...},
            "output_schema": {...}
        },
        {
            "name": "grader_tool",
            "arn": "lambda-arn-for-grader",
            "region": "us-east-1",
            "input_schema": {...},
            "output_schema": {...}
        }
    ],
    "model": "llama3",
    "supported_llms": ["gpt-3.5", "llama3"],
    "entry_point": "retriever_tool",
    "nodes": [
        {
            "name": "retriever_tool",
            "destination": "grader_tool"
        },
        {
            "name": "grader_tool",
            "destination": "END"
        }
    ]
}
