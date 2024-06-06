docs = vector_db.similarity_search_with_relevance_scores(
    query=rw.user_query,
    k=rw.num_of_citations,
    score_threshold=score_threshold,
    **({'pre_filter': search_kwargs, 'search_type': 'painless_scripting', 'space_type': 'cosine'} if search_type == 'painless_scripting' and space_type == 'cosine' else {'filter': search_kwargs})
)
