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
