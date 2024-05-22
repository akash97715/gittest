class IASOpenaiEmbeddings(Embeddings):
    """Wrapper for IAS secured OpenAI embedding API"""
 
    engine = str
    client_id: str = None
    x_vsl_client_id: str = None
    bearer_auth: str = None
    totalToken:list
 
    def __init__(self, engine, client_id,totalToken, x_vsl_client_id=None, bearer_auth=None):
        self.engine = engine
        self.totalToken=totalToken
        self.client_id = client_id
        self.x_vsl_client_id = x_vsl_client_id
        self.bearer_auth = bearer_auth
 
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeddings search docs."""
        # NOTE: to keep things simple, we assume the list may contain texts longer
        #       than the maximum context and use length-safe embedding function.
 
        response, totaltok = ias_openai_embeddings(
            texts, self.engine, self.client_id, self.x_vsl_client_id, self.bearer_auth
        )
        self.totalToken.append(totaltok)
 
        # Extract the embeddings
        embeddings: list[list[float]] = [data["embedding"] for data in response]
        return embeddings
 
    def embed_query(self, text: str) -> List[float]:
        """Embeddings  query text."""
 
        response, totaltok = ias_openai_embeddings(
            text, self.engine, self.client_id, self.x_vsl_client_id, self.bearer_auth
        )
        self.totalToken.append(totaltok)
 
        # Extract the embeddings and total tokens
        embeddings: list[list[float]] = [data["embedding"] for data in response]
        return embeddings[0]
