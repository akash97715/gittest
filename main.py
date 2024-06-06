search_kwargs_dict = {'filter': search_kwargs}

if rw.search_type == 'painless_scripting':
    search_kwargs_dict = {'pre_filter': search_kwargs, 'search_type': 'painless_scripting'}
    if rw.space_type:
        search_kwargs_dict['space_type'] = rw.space_type

search_params = {
    'query': rw.user_query,
    'k': rw.num_of_citations,
    'score_threshold': score_threshold,
    **search_kwargs_dict
}

# Print or log the search parameters
print("Search parameters:", search_params)

# Perform the search
docs = vector_db.similarity_search_with_score(**search_params)
