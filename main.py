Tool
 
"agent":"retriever_agent",
 
 
{
    "id":1,
    "name":"retriever_tool",
    "desc": "Retrieves data from the database",
    "type":"tool",
    "lambda_arn":"arn:aws:lambda:us-east-1:123456789012:function:retriever_tool",
    "req_payload": {},
    "res_payload": {}
}
 
Agents
 
{
    "id":1,
    "name":"retriever_agent",
    "desc": "Retrieves data from the database",
    "type":"agent",
    "prompt":"What data would you like to retrieve?",
    "sys_prompt": "What data would you like to retrieve?",
    "tools":[1],
    "llm":"",
    "supported_llm":"",
    // "nodes": {},
    "edges": [{
        "start_node": "retriever_tool",
        "end_node": "grade_tool",
    },
    {
        "start_node": "grade_tool",
        "conditions": [{
            "condition": "NO",
            "start_node": "retriever_tool"
        },{
            "condition": "Yes",
            "start_node": "retriever_tool"
        }],
        "end_node": "LLM",
    },
    {
        "start_node": "LLM",
        "conditions": {
            "condition": "NO",
            "start_node": "retriever_tool"
        },
        "end_node": "END",
    }],
    "entry_point": "retriever_tool",
}
