import pandas as pd

# Sample DataFrame
data = {
    'id': range(100),
    'value': [f'value_{i}' for i in range(100)]
}
df = pd.DataFrame(data)

# Initialize a new column for responses
df['response'] = None

# Assuming you have a list of 15 responses to update at once
responses_list = [
    ['response_1', 'response_2', 'response_3', 'response_4', 'response_5',
     'response_6', 'response_7', 'response_8', 'response_9', 'response_10',
     'response_11', 'response_12', 'response_13', 'response_14', 'response_15']
]

# Update the DataFrame in chunks of 15 using iloc
batch_size = 15

for start in range(0, len(df), batch_size):
    end = start + batch_size
    batch_indices = df.index[start:end]
    
    # Make sure we only update if we have a full batch of responses
    if len(batch_indices) == batch_size:
        # Replace the following line with your actual list of responses for each batch
        responses = responses_list[0]  # Example for the first batch
        
        # Update the DataFrame using iloc, ensuring the correct alignment
        df.iloc[start:end, df.columns.get_loc('response')] = responses[:len(batch_indices)]

print(df)
