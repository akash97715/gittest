docs = vector_db.similarity_search_with_relevance_scores(
    query=rw.user_query,
    k=rw.num_of_citations,
    score_threshold=score_threshold,
    space_type=space_type,
    **({'pre_filter': search_kwargs, 'search_type': 'painless_scripting'} if search_type == 'painless_scripting' else {'filter': search_kwargs})
)
