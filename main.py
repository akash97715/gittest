import openai

# Set your API key
openai.api_key = 'your-api-key'

# Function to get a chat completion from OpenAI
def get_chat_completion(prompt, model="gpt-4", max_tokens=100):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=1.0,
    )
    return response.choices[0].message['content']

# Example prompt
prompt = "Can you explain the theory of relativity in simple terms?"

# Get the response from OpenAI
response = get_chat_completion(prompt)

# Print the response
print(response)
