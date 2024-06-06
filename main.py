search_params = {
    'query': rw.user_query,
    'k': rw.num_of_citations,
    'score_threshold': score_threshold,
    **({'pre_filter': search_kwargs, 'search_type': 'painless_scripting', 'space_type': rw.space_type} if rw.search_type == 'painless_scripting' else {'filter': search_kwargs})
}

if rw.space_type:
    search_params['space_type'] = rw.space_type

# Print or log the search parameters
print("Search parameters:", search_params)

# Perform the search
docs = vector_db.similarity_search_with_score(**search_params)
