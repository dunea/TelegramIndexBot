import meilisearch
from meilisearch.index import Index


class MeiliSearch:
    def __init__(self, url: str, api_key: str):
        self.client = meilisearch.Client(url, api_key=api_key)
        self.index = self._index_index()
    
    def _index_index(self) -> Index:
        index = self.client.index('index')
        
        index.update_filterable_attributes([
            'type',
            'count_members',
            'last_gather_at',
        ])
        
        index.update_searchable_attributes([
            'nickname',
            'desc',
        ])
        
        return index
