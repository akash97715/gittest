---------------------------------------------------------------------------BulkIndexError                            Traceback (most recent call last)Cell In[41],
line 39
    
34
         batch_metadatas = metadatas[i:i+batch_size]    
35
         add_embeddings_func(text_embeddings=batch_text_embeddings, metadatas=batch_metadatas)--->
39
process_in_batches(vector_db.add_embeddings, text_embeddings, metadatas, batch_size) Cell In[41],
line 35
    
33
batch_text_embeddings = text_embeddings[i:i+batch_size]    
34
batch_metadatas = metadatas[i:i+batch_size]--->
35
add_embeddings_func(text_embeddings=batch_text_embeddings, metadatas=batch_metadatas) File
d:\docinsightenv\Lib\site-packages\langchain_community\vectorstores\opensearch_vector_search.py:448
, in OpenSearchVectorSearch.add_embeddings(self, text_embeddings, metadatas, ids, bulk_size, **kwargs)   
428
"""Add the given texts and embeddings to the vectorstore.   
429
   
430
Args:   (...)   
445
    to "text".   
446
"""   
447
texts, embeddings = zip(*text_embeddings)-->
448
return self.__add(   
449
     list(texts),   
450
     list(embeddings),   
451
     metadatas=metadatas,   
452
     ids=ids,   
453
     bulk_size=bulk_size,   
454
     **kwargs,   
455
) File
d:\docinsightenv\Lib\site-packages\langchain_community\vectorstores\opensearch_vector_search.py:370
, in OpenSearchVectorSearch.__add(self, texts, embeddings, metadatas, ids, bulk_size, **kwargs)   
364
_validate_aoss_with_engines(self.is_aoss, engine)   
366
mapping = _default_text_mapping(   
367
     dim, engine, space_type, ef_search, ef_construction, m, vector_field   
368
)-->
370
return _bulk_ingest_embeddings(   
371
     self.client,   
372
     index_name,   
373
     embeddings,   
374
     texts,   
375
     metadatas=metadatas,   
376
     ids=ids,   
377
     vector_field=vector_field,   
378
     text_field=text_field,   
379
     mapping=mapping,   
380
     max_chunk_bytes=max_chunk_bytes,   
381
     is_aoss=self.is_aoss,   
382
) File
d:\docinsightenv\Lib\site-packages\langchain_community\vectorstores\opensearch_vector_search.py:138
, in _bulk_ingest_embeddings(client, index_name, embeddings, texts, metadatas, ids, vector_field, text_field, mapping, max_chunk_bytes, is_aoss)   
136
     requests.append(request)   
137
     return_ids.append(_id)-->
138
bulk(client, requests, max_chunk_bytes=max_chunk_bytes)   
139
if not is_aoss:   
140
     client.indices.refresh(index=index_name) File
d:\docinsightenv\Lib\site-packages\opensearchpy\helpers\actions.py:425
, in bulk(client, actions, stats_only, ignore_status, *args, **kwargs)   
423
# make streaming_bulk yield successful results so we can count them   
424
kwargs["yield_ok"] = True-->
425
for ok, item in streaming_bulk(client, actions, ignore_status=ignore_status, *args, **kwargs):  # type: ignore   
426
     # go through request-response pairs and detect failures   
427
     if not ok:   
428
         if not stats_only: File
d:\docinsightenv\Lib\site-packages\opensearchpy\helpers\actions.py:338
, in streaming_bulk(client, actions, chunk_size, max_chunk_bytes, raise_on_error, expand_action_callback, raise_on_exception, max_retries, initial_backoff, max_backoff, yield_ok, ignore_status, *args, **kwargs)   
335
     time.sleep(min(max_backoff, initial_backoff * 2 ** (attempt - 1)))   
337
try:-->
338
     for data, (ok, info) in zip(   
339
         bulk_data,   
340
         _process_bulk_chunk(   
341
             client,   
342
             bulk_actions,   
343
             bulk_data,   
344
             raise_on_exception,   
345
             raise_on_error,   
346
             ignore_status,   
347
             *args,   
348
             **kwargs   
349
         ),   
350
     ):   
351
         if not ok:   
352
             action, info = info.popitem() File
d:\docinsightenv\Lib\site-packages\opensearchpy\helpers\actions.py:273
, in _process_bulk_chunk(client, bulk_actions, bulk_data, raise_on_exception, raise_on_error, ignore_status, *args, **kwargs)   
266
else:   
267
     gen = _process_bulk_chunk_success(   
268
         resp=resp,   
269
         bulk_data=bulk_data,   
270
         ignore_status=ignore_status,   
271
         raise_on_error=raise_on_error,   
272
     )-->
273
for item in gen:   
274
     yield item File
d:\docinsightenv\Lib\site-packages\opensearchpy\helpers\actions.py:202
, in _process_bulk_chunk_success(resp, bulk_data, ignore_status, raise_on_error)   
199
         yield ok, {op_type: item}   
201
if errors:-->
202
     raise BulkIndexError("%i document(s) failed to index." % len(errors), errors) BulkIndexError: ('12 document(s) failed to index.', [{'index': {'_index': 'reingest', '_id': 'c7cc7c73-d3e5-4f29-9351-c5649805c06f',
