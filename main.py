elif self.search_type == "similarity_score_threshold":
            docs_and_similarities = (
                self.vectorstore.similarity_search_with_relevance_scores(
                    query, **self.search_kwargs
                )
            )
            docs = [doc for doc, _ in docs_and_similarities]
           
            if self.parent_document_retriever:
                ids = []
                for d in docs:
                    if d.metadata[self.id_key] not in ids:
                        print("tree234")
                        ids.append(d.metadata[self.id_key])
               
                docs = self.docstore.mget(ids)
                docs = [d for d in docs if d is not None]
 
        elif self.search_type == "mmr":
            docs = self.vectorstore.max_marginal_relevance_search(
                query, **self.search_kwargs
            )
        else:
            raise ValueError(f"search_type of {self.search_type} not allowed.")
        return docs
