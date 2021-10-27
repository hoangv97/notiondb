
from .database import NotionDatabase
from typing import List


class QuerySet:

    def __init__(self, model_cls, database: NotionDatabase):
        self.model_cls = model_cls
        self.database = database

    def get(self, filter: dict = None, sorts: List[dict] = None, limit: int = None):
        cnt = 0
        for item in self.database.find(filter, sorts):
            if limit is None or cnt < limit:
                yield self.model_cls.from_data(self.database, item)
                cnt += 1
