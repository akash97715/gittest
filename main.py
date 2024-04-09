from typing import Iterator, Sequence, Tuple, TypeVar, List, Optional
from langchain_core.stores import BaseStore
from langchain_core.documents import Document
import json
from opensearchpy import OpenSearch

K = TypeVar("K")
V = TypeVar("V")

class OpenSearchDocStore(BaseStore):
    def __init__(self, host: str, port: int, index_name: str, use_ssl: bool = True, http_auth: Tuple[str, str] = None):
        self.index_name = index_name
        self.client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_compress=True,  # Enables gzip compression for request bodies
            use_ssl=use_ssl,
            http_auth=http_auth,
            verify_certs=True
        )
        # Ensure the index exists
        self._create_index_if_not_exists()

    def _create_index_if_not_exists(self):
        """Creates an index if it doesn't already exist."""
        if not self.client.indices.exists(index=self.index_name):
            self.client.indices.create(index=self.index_name)

    def mset(self, key_value_pairs: Sequence[Tuple[K, V]]) -> None:
        """Index documents in the OpenSearch index."""
        for key, document in key_value_pairs:
            print("Indexing document with key:", key)
            self.client.index(index=self.index_name, id=key, document=json.dumps(dict(document)))

    def mget(self, keys: Sequence[K]) -> List[Optional[V]]:
        """Retrieve documents from the OpenSearch index by keys."""
        print("Retrieving documents for keys:", keys)
        responses = []
        for key in keys:
            result = self.client.get(index=self.index_name, id=key, ignore=[404])
            if result['found']:
                responses.append(Document(**json.loads(result['_source'])))
            else:
                responses.append(None)
        return responses

    def mdelete(self, keys: Sequence[K]) -> None:
        """Delete documents from the OpenSearch index by keys."""
        for key in keys:
            print("Deleting document with key:", key)
            self.client.delete(index=self.index_name, id=key, ignore=[404])

    def yield_keys(self, *, prefix: str | None = None) -> Iterator[K]:
        """Yields keys from the OpenSearch index, optionally filtered by a prefix."""
        query = {"query": {"match_all": {}}} if prefix is None else {"query": {"prefix": {"_id": prefix}}}
        resp = self.client.search(index=self.index_name, body=query, scroll='1m', size=1000)
        scroll_id = resp['_scroll_id']
        while True:
            results = resp['hits']['hits']
            if not results:
                break
            for result in results:
                yield result['_id']
            resp = self.client.scroll(scroll_id=scroll_id, scroll='1m')
