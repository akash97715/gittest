from langchain.agents import create_react_agent
from langchain_openai import OpenAI

# Assuming 'loaded_tools' contains the tools you loaded earlier
llm = OpenAI(temperature=0)

# Create an agent using the new method
agent = create_react_agent(
    llm=llm,
    tools=loaded_tools,
    verbose=True
)

# Use the agent
response = agent.run("Send an email to test@testing123.com saying hello world.")
print(response)
