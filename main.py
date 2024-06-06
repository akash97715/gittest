[6:48 PM] Deep, Akash (External)
docs = vector_db.similarity_search_with_score(
                        query=rw.user_query,
                        k=rw.num_of_citations,
                        score_threshold=score_threshold,
                        space_type=rw.space_type,
                        **({'pre_filter': search_kwargs, 'search_type': 'painless_scripting'} if rw.search_type == 'painless_scripting' else {'filter': search_kwargs})
                    )
