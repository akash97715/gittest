{
    "name": "Dummy Agent",
    "type": "agent",
    "prompt": "What is the meaning of life?",
    "system_prompt": "Assume that you are a philosopher heavily influenced by Socrates and believe in equilibrium between liberal and capitalist ideas.",
    "tools": [
        { "name": "tool1", "method": "GET", "arn": "ASFGAGSDHDSHHDHH-adaHdh" },
        { "name": "tool2", "method": "POST", "arn": "ASFGAGSDHDSHHDHH-adaHdh" },
        { "name": "tool3", "method": "PUT", "arn": "ASFGAGSDHDSHHDHH-adaHdh" },
        { "name": "tool4", "method": "GET", "arn": "ASFGAGSDHDSHHDHH-adaHdh" },
        { "name": "tool5", "method": "GET", "arn": "ASFGAGSDHDSHHDHH-adaHdh" },
        { "name": "rewrite", "method": "GET", "arn": "ASFGAGSDHDSHHDHH-adaHdh" }
    ],
    "model": "llama3",
    "entry_point": "tool1",
    "nodes": [
        {
            "name": "tool1",
            "destination": "tool2"
        },
        {
            "name": "tool2",
            "destination": "tool3"
        },
        {
            "name": "tool3",
            "condition": {
                "deciding_fn": "rewrite",
                "process": "tool4",
                "exit": "END"
            }
        },
        {
            "name": "tool4",
            "destination": "tool1"
        }
    ]
}
