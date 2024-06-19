config = {
    "name": "Dummy Agent",
    "type": "agent",
    "prompt": "What is the meaning of life?",
    "system_prompt": "Assume that you are a philosopher heavily influenced by Socrates and believe in equilibrium between liberal and capitalist ideas.",
    "tools": [
        { "name": "retrieve", "method": "GET", "arn": "arn:aws:lambda:region:account-id:function:retrieve", "region": "your-region" },
        { "name": "grade_documents", "method": "POST", "arn": "arn:aws:lambda:region:account-id:function:grade_documents", "region": "your-region" },
        { "name": "generate", "method": "PUT", "arn": "arn:aws:lambda:region:account-id:function:generate", "region": "your-region" },
        { "name": "transform_query", "method": "GET", "arn": "arn:aws:lambda:region:account-id:function:transform_query", "region": "your-region" },
        { "name": "decide_to_generate", "method": "GET", "arn": "arn:aws:lambda:region:account-id:function:decide_to_generate", "region": "your-region" },
        { "name": "grade_generation_v_documents_and_question", "method": "GET", "arn": "arn:aws:lambda:region:account-id:function:grade_generation_v_documents_and_question", "region": "your-region" },
        { "name": "grade_documents_enhanced", "method": "POST", "arn": "arn:aws:lambda:region:account-id:function:grade_documents_enhanced", "region": "your-region" }
    ],
    "model": "llama3",
    "entry_point": "retrieve",
    "nodes": [
        {
            "name": "retrieve",
            "destination": "grade_documents"
        },
        {
            "name": "grade_documents",
            "condition": {
                "deciding_fn": "decide_to_generate",
                "process": {
                    "transform_query": "transform_query",
                    "generate": "generate",
                    "failure": "grade_documents_enhanced"
                }
            }
        },
        {
            "name": "transform_query",
            "destination": "retrieve"
        },
        {
            "name": "generate",
            "condition": {
                "deciding_fn": "grade_generation_v_documents_and_question",
                "process": {
                    "not supported": "generate",
                    "useful": END,
                    "not useful": "transform_query"
                }
            }
        },
        {
            "name": "grade_documents_enhanced",
            "destination": "generate"
        }
    ]
}
