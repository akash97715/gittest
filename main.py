metering_dict = [{'engine': rw.embedding_engine, 'total_token': total_token[1]}] + ([{'engine': rw.llm_engine, 'total_token': total_token[0]}] if llm_response_flag else [])
