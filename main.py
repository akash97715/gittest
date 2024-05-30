  for doc in parent_documents:
                    _id = "{}/{}/{}".format(self.client_id, self.index_name, uuid.uuid4())
                    sub_docs = text_splitter.split_documents([doc])
 
                    for _doc in sub_docs:
                        _doc.metadata[self.parent_doc_id_key] = _id
 
                    docs.extend(sub_docs)
                    full_docs.append((_id, doc))
 
                return full_docs, docs
 
            return [], text_splitter.split_documents(pages)
