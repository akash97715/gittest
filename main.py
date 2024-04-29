enhanced_docs = [doc for doc in enhanced_docs if doc is not None]
            logger.debug(
                f"{len(enhanced_docs)} docs fetched using parent-child retriever"
            )
