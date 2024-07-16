{
    "name": "Dummy Agent",
    "description": "agent",
    "prompt": "What is the meaning of life?",
    "system_prompt": "Assume that you are a philosopher heavily influenced by Socrates and believe in equilibrium between liberal and capitalist ideas.",
    "tools": [
        {
            "name": "retriever_tool",
            "arn": "ASFGAGSDHDSHHDHH-adaHdh",
            "region": "us-east-1",
            "input_schema": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"},
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of fields to retrieve (e.g., ['name', 'price', 'description'])"
                    }
                },
                "required": ["product_id"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"},
                    "name": {"type": "string"},
                    "price": {"type": "number"},
                    "description": {"type": "string"},
                    "in_stock": {"type": "boolean"}
                },
                "required": ["product_id", "name", "price"]
            }
        },
        {
            "name": "grader_tool",
            "arn": "ASFGAGSDHDSHHDHH-adaHdh",
            "region": "us-east-1",
            "input_schema": {
                "type": "object",
                "properties": {
                    "grade_id": {"type": "string"},
                    "scores": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "List of scores to evaluate"
                    }
                },
                "required": ["grade_id"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "grade_id": {"type": "string"},
                    "total": {"type": "number"},
                    "passed": {"type": "boolean"},
                    "details": {"type": "string"}
                },
                "required": ["grade_id", "total", "passed"]
            }
        }
        // Add additional tools configuration here following the pattern above
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
            "condition": {
                "deciding_fn": "how_is_it",
                "destination": {
                    "bad": "rewriter_tool",
                    "good": "send_chunks_tool"
                }
            }
        },
        {
            "name": "rewriter_tool",
            "destination": "retriever_tool"
        },
        {
            "name": "send_chunks_tool",
            "destination": "END"
        }
    ]
}
