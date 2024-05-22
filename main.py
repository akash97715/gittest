llm_class = (
            IASOpenaiConversationalLLM
            if llm_engine.startswith("gpt")
            else IASBedrockLLM
        )
        qa = IAS_ConversationalRetrievalChain.from_llm(
            llm_class(**llm_config),
            chain_type="stuff",
            retriever=vector_db,
            return_source_documents=True,
            max_tokens_limit=calculate_max_tokens(
                max_tokens, str(llm_engine), min_response_token
            ),
            response_if_no_docs_found=(
                answer_if_no_docs_found if vector_score_threshold else None
            ),
            llm_response_flag=llm_response_flag,
            answer_from_llm_if_no_docs_found=answer_from_llm_if_no_docs_found,
        )
       
 
        chat_history = create_chat_history(context)
 
        if answer_from_llm_if_no_docs_found:
            # Added for Vox Flow.
            answer_with_llm_knowledge = "If you don't know the answer, then answer from your own knowledge base."
        else:
            answer_with_llm_knowledge = "If you don't know the answer, just say that you don't know, don't try to make up an answer."
 
        llm_response = qa(
            {
                "question": user_query,
                "chat_history": chat_history,
                "answer_with_llm_knowledge": answer_with_llm_knowledge,
            }
        )
