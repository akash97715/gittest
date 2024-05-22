from typing import List

class IASOpenaiEmbeddings(Embeddings):
    """Wrapper for IAS secured OpenAI embedding API"""
    
    engine = str
    client_id: str = None
    x_vsl_client_id: str = None
    bearer_auth: str = None
    totalToken: list
    
    def __init__(self, engine, client_id, totalToken, x_vsl_client_id=None, bearer_auth=None):
        self.engine = engine
        self.totalToken = totalToken
        self.client_id = client_id
        self.x_vsl_client_id = x_vsl_client_id
        self.bearer_auth = bearer_auth
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds search docs."""
        try:
            response, totaltok = ias_openai_embeddings(
                texts, self.engine, self.client_id, self.x_vsl_client_id, self.bearer_auth
            )
            self.totalToken.append(totaltok)
            
            # Extract the embeddings
            embeddings: list[list[float]] = [data["embedding"] for data in response]
            return embeddings
        except Exception as e:
            self.handle_error(e)
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """Embeds query text."""
        try:
            response, totaltok = ias_openai_embeddings(
                text, self.engine, self.client_id, self.x_vsl_client_id, self.bearer_auth
            )
            self.totalToken.append(totaltok)
            
            # Extract the embeddings
            embeddings: list[list[float]] = [data["embedding"] for data in response]
            return embeddings[0]
        except Exception as e:
            self.handle_error(e)
            raise
    
    def handle_error(self, error: Exception):
        """Handles errors by calling push_metric with the sum of totalToken."""
        total_tokens_sum = sum(self.totalToken)
        self.push_metric(total_tokens_sum)
    
    def push_metric(self, total_tokens: int):
        """Placeholder function to push metrics."""
        print(f"Pushing metric: Total Tokens = {total_tokens}")
