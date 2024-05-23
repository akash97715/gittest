import pandas as pd

class FileLoader:
    def __init__(self, chunks: List[str], metadata: List[str], parquet_path: str):
        self.chunks = chunks
        self.metadata = metadata
        self.parquet_path = parquet_path

    def create_parquet(self):
        # Create a DataFrame with the initial data
        data = {
            'chunk': self.chunks,
            'metadata': self.metadata,
            'embedding': [None] * len(self.chunks),
            'status': [''] * len(self.chunks)
        }
        df = pd.DataFrame(data)
        
        # Save the DataFrame to a Parquet file
        df.to_parquet(self.parquet_path, index=False)
        print(f"Parquet file created at {self.parquet_path}")

# Example usage
chunks = ["chunk1", "chunk2", "chunk3"]
metadata = ["metadata1", "metadata2", "metadata3"]
parquet_path = "path/to/your_initial.parquet"

file_loader = FileLoader(chunks, metadata, parquet_path)
file_loader.create_parquet()
