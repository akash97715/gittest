def embed(texts):
    """
    Generate embeddings for a list of text documents in batches.
 
    This function assumes the existence of an `embd` object with a method `embed_documents`
    that takes a list of texts and returns their embeddings.
 
    Parameters:
    - texts: List[str], a list of text documents to be embedded.
 
    Returns:
    - numpy.ndarray: An array of embeddings for the given text documents.
    """
    batch_size = 15
    text_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        print("Processing batch:", batch)  # Debug print to show the current batch
        batch_embeddings = embd.embed_documents(batch)
        text_embeddings.extend(batch_embeddings)
    
    text_embeddings_np = np.array(text_embeddings)
    return text_embeddings_np

def embed_cluster_texts(texts):
    """
    Embeds a list of texts and clusters them, returning a DataFrame with texts, their embeddings, and cluster labels.
 
    This function combines embedding generation and clustering into a single step. It assumes the existence
    of a previously defined `perform_clustering` function that performs clustering on the embeddings.
 
    Parameters:
    - texts: List[str], a list of text documents to be processed.
 
    Returns:
    - pandas.DataFrame: A DataFrame containing the original texts, their embeddings, and the assigned cluster labels.
    """
    text_embeddings_np = embed(texts)  # Generate embeddings
    cluster_labels = perform_clustering(
        text_embeddings_np, 10, 0.1
    )  # Perform clustering on the embeddings
    df = pd.DataFrame()  # Initialize a DataFrame to store the results
    df["text"] = texts  # Store original texts
    df["embd"] = list(text_embeddings_np)  # Store embeddings as a list in the DataFrame
    df["cluster"] = cluster_labels  # Store cluster labels
    return df
