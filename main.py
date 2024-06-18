import pandas as pd

# Load the parquet file
file_path = '/mnt/data/Screenshot 2024-06-18 at 9.40.42 AM.png'  # Update this to the actual file path if it's different
df = pd.read_parquet(file_path)

# Define the batch size
batch_size = 500

# Prepare the parameters for the add_embeddings function
text_embeddings = list(zip(df['chunk'], df['embedding']))
metadatas = df['metadata'].tolist()

# Function to add embeddings in batches
def process_in_batches(add_embeddings_func, text_embeddings, metadatas, batch_size):
    for i in range(0, len(text_embeddings), batch_size):
        batch_text_embeddings = text_embeddings[i:i+batch_size]
        batch_metadatas = metadatas[i:i+batch_size]
        add_embeddings_func(text_embeddings=batch_text_embeddings, metadatas=batch_metadatas)

# Assuming add_embeddings is a method of an instantiated class, use `instance.add_embeddings`
# Replace `instance` with the actual instance of the class
process_in_batches(instance.add_embeddings, text_embeddings, metadatas, batch_size)
