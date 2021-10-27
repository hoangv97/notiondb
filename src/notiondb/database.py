
from .api import NotionApi
from .block_parser import BlockParser
from .consts import *
from .block import BaseBlock
from .fields import BaseField
from typing import List


class NotionDatabase(object):

    def __init__(self, token: str, database_id: str = None, parent_id: str = None, title: str = None, properties: List[BaseField] = None):
        self.api = NotionApi(token)

        self.id = database_id

        if parent_id and title and properties:
            props_obj = {}
            for prop in properties:
                props_obj.update(prop.get_creating_database_prop())
            
            info = self.api.create_database(parent_id, title, properties=props_obj)
            self.id = info.get('id')

    def parse_database(self, db: dict):
        if db and 'title' in db:
            db['title'] = ''.join([line.get('plain_text', '') for line in db['title']])
        return db

    def all(self):
        databases = self.api.get_databases()
        databases = list(map(self.parse_database, databases))
        return databases

    def info(self):
        info = self.api.get_database(self.id)
        info = self.parse_database(info)
        return info

    def update_database(self, title: str):
        info = self.api.update_database(self.id, title=title)
        info = self.parse_database(info)
        return info

    def get_children(self, id: str):
        blocks, next_cursor = self.api.get_block_children(id)
        while next_cursor:
            _blocks, next_cursor = self.api.get_block_children(id, start_cursor=next_cursor)
            blocks += _blocks

        children = []

        for block in blocks:
            if block.get('has_children'):
                block['children'] = self.get_children(block.get('id'))

            children.append(block)

        return children

    def parse_item(self, item: dict, includes_children=True):
        result = {
            '_id': item.get('id'),
        }
        if item.get('archived'):
            result.update({
                '_archived': True,
            })
        properties = item.get('properties', {})
        for prop in properties.keys():
            result[prop] = BlockParser(properties[prop]).value

        if includes_children:
            result['children'] = self.get_children(item.get('id'))

        return result

    def find(self, filter: dict = None, sorts: List[dict] = None, start_cursor: str = None, page_size: int = None, includes_children=False):
        rows, next_cursor = self.api.query_database(self.id, filter=filter, sorts=sorts, start_cursor=start_cursor, page_size=page_size)
        for row in rows:
            yield self.parse_item(row, includes_children)

        if next_cursor:
            yield from self.find(filter=filter, sorts=sorts, start_cursor=next_cursor, page_size=page_size, includes_children=includes_children)

    def find_one(self, id: str, includes_children=False):
        item = self.api.get_page(id)
        if item:
            return self.parse_item(item, includes_children=includes_children)
        return None

    def update_one(self, id: str, properties: dict):
        item = self.api.update_page(id, properties=properties)
        if item:
            return self.parse_item(item, includes_children=False)
        return None

    def append_children(self, id: str, blocks: List[BaseBlock]):
        children = [block.value for block in blocks]
        item = self.api.append_block_children(id, children=children)
        if item:
            return self.parse_item(item, includes_children=False)
        return None

    def insert_one(self, properties: dict, children: List[dict] = None):
        item = self.api.create_page('database_id', self.id, properties=properties, children=children)
        if item:
            return self.parse_item(item, includes_children=False)
        return None

    def delete_one(self, id: str):
        item = self.api.update_page(id, archived=True)
        if item:
            return self.parse_item(item, includes_children=False)
        return None

    def delete_many(self, ids: List[str]):
        result = []
        for id in ids:
            item = self.delete_one(id=id)
            if item:
                result.append(item)
        return result

