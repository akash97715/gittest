search_type: Optional[str]='approximate_search'
 
 docs = vector_db.similarity_search_with_relevance_scores(
                query=rw.user_query,
                k=rw.num_of_citations,
                filter=search_kwargs,
                score_threshold=score_threshold,
            )
