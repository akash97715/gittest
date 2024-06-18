import pandas as pd

# Sample DataFrame
data = {
    'id': range(100),
    'value': [f'value_{i}' for i in range(100)]
}
df = pd.DataFrame(data)

# Function to process a batch of items
def process_batch(batch):
    # Simulate processing
    responses = [f'response_{item["id"]}' for index, item in batch.iterrows()]
    return responses

# Function to update DataFrame with responses
def update_dataframe(df, indices, responses):
    for i, response in zip(indices, responses):
        df.at[i, 'response'] = response

# Main batch processing logic
batch_size = 15
df['response'] = None  # Initialize a new column for responses

for start in range(0, len(df), batch_size):
    end = start + batch_size
    batch = df.iloc[start:end]
    responses = process_batch(batch)
    update_dataframe(df, batch.index, responses)

print(df)
