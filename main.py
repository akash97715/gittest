elif self.search_type == "similarity_score_threshold":
    docs_and_similarities = self.vectorstore.similarity_search_with_relevance_scores(
        query, **self.search_kwargs
    )
    docs = [doc for doc, _ in docs_and_similarities]

    # Collect IDs from documents that contain self.id_key in metadata
    ids = set(d.metadata[self.id_key] for d in docs if self.id_key in d.metadata)

    # Retrieve the enhanced documents using mget if any IDs are available
    enhanced_docs = self.docstore.mget(list(ids)) if ids else []

    # Ensure all retrieved documents from mget are valid (not None)
    enhanced_docs = [doc for doc in enhanced_docs if doc is not None]

    # Combine enhanced docs with original docs, excluding any original docs that have been enhanced
    final_docs = enhanced_docs + [doc for doc in docs if self.id_key not in doc.metadata or doc.metadata[self.id_key] not in ids]

elif self.search_type == "mmr":
    final_docs = self.vectorstore.max_marginal_relevance_search(
        query, **self.search_kwargs
    )

else:
    raise ValueError(f"search_type of {self.search_type} not allowed.")

return final_docs
