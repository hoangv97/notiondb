from typing import List, Literal
import requests


class ResponseDecorators:

    def __init__(self):
        pass

    @staticmethod
    def get_result(response: requests.Response):
        if response.status_code != 200:
            return None
        result: dict = response.json()
        return result

    @staticmethod
    def object(func):
        def wrapper(*args, **kwargs):
            return ResponseDecorators.get_result(func(*args, **kwargs))
        
        return wrapper

    @staticmethod
    def pagination(func):
        def wrapper(*args, **kwargs):
            result = ResponseDecorators.get_result(func(*args, **kwargs))
            if not result:
                return None, None
            return result.get('results', []), result.get('next_cursor', None)
        
        return wrapper

class NotionApi:

    URL_PREFIX = 'https://api.notion.com/v1/'

    NOTION_VERSION = '2021-08-16'

    def __init__(self, token: str, notion_version: str = None):
        self.token = token
        if notion_version:
            self.NOTION_VERSION = notion_version

    @property
    def headers(self):
        return {
            'Authorization': self.token,
            'Notion-Version': self.NOTION_VERSION,
        }

    @ResponseDecorators.pagination
    def search(self, object: Literal['database', 'page'], query: str = None, start_cursor: str = None, page_size: int = None):
        url = f'{self.URL_PREFIX}search'
        data = {
            'filter': {
                'property': 'object',
                'value': object
            }
        }
        if query:
            data['query'] = query
        if start_cursor:
            data['start_cursor'] = start_cursor
        if page_size:
            data['page_size'] = page_size
        
        return requests.post(url, headers=self.headers, json=data)

    """
    DATABASES
    """
    def get_databases(self, query: str = None, start_cursor: str = None, page_size: int = None):
        return self.search('database', query=query, start_cursor=start_cursor, page_size=page_size)

    @ResponseDecorators.object
    def create_database(self, parent_id: str, title: str, properties: dict):
        url = f'{self.URL_PREFIX}databases'
        data = {
            'parent': {
                'type': 'page_id',
                'page_id': parent_id,
            },
            'properties': properties,
            'title': [
                {
                    'type': 'text',
                    'text': {
                        'content': title,
                        'link': None
                    }
                }
            ]
        }
        return requests.post(url, headers=self.headers, json=data)

    @ResponseDecorators.object
    def get_database(self, id: str):
        url = f'{self.URL_PREFIX}databases/{id}'
        return requests.get(url, headers=self.headers)

    @ResponseDecorators.object
    def update_database(self, id: str, title: str = None, properties: dict = None):
        url = f'{self.URL_PREFIX}databases/{id}'
        data = {}
        if title:
            data.update({
                'title': [
                    {
                        'text': {
                            'content': title
                        }
                    }
                ]
            })
        if properties:
            data.update({
                'properties': properties
            })
        
        return requests.patch(url, headers=self.headers, json=data)

    """
    https://developers.notion.com/reference/post-database-query#post-database-query-filter
    """
    @ResponseDecorators.pagination
    def query_database(self, id, filter: dict = None, sorts: List[dict] = None, start_cursor: str = None, page_size: int = None):
        url = f'{self.URL_PREFIX}databases/{id}/query'
        data = {}
        if filter:
            data['filter'] = filter
        if sorts:
            data['sorts'] = sorts
        if start_cursor:
            data['start_cursor'] = start_cursor
        if page_size:
            data['page_size'] = page_size

        return requests.post(url, headers=self.headers, json=data)

    """
    PAGES
    """
    def get_pages(self, query: str = None, start_cursor: str = None, page_size: int = None):
        return self.search('page', query=query, start_cursor=start_cursor, page_size=page_size)

    @ResponseDecorators.object
    def get_page(self, id: str):
        url = f'{self.URL_PREFIX}pages/{id}'
        return requests.get(url, headers=self.headers)

    """
    https://developers.notion.com/reference/page#page-property-value
    """
    @ResponseDecorators.object
    def update_page(self, id: str, properties: dict = None, archived: bool = None):
        url = f'{self.URL_PREFIX}pages/{id}'
        data = {}
        if properties:
            data.update({
                'properties': properties
            })
        if archived is not None:
            data.update({
                'archived': archived
            })
        return requests.patch(url, headers=self.headers, json=data)

    @ResponseDecorators.object
    def create_page(self, parent_type: Literal['database_id', 'page_id'], parent_id: str, title: str = None, properties: dict = {}, children: List[dict] = None, icon: str = None, cover: str = None):
        url = f'{self.URL_PREFIX}pages'
        
        if title:
            properties.update({
                'title': [
                    {
                        'text': {
                            'content': title
                        }
                    }
                ]
            })

        data = {
            'parent': {
                parent_type: parent_id,
            },
            'properties': properties,
        }

        if children:
            data.update({
                'children': children,
            })
        if icon:
            data.update({
                'icon': {
                    'type': 'emoji',
                    'emoji': icon
                },
            })
        if cover:
            data.update({
                'cover': {
                    'type': 'external',
                    'external': {
                        'url': cover
                    }
                },
            })
        return requests.post(url, headers=self.headers, json=data)

    @ResponseDecorators.object
    def get_block(self, id: str):
        url = f'{self.URL_PREFIX}blocks/{id}'
        return requests.get(url, headers=self.headers)

    @ResponseDecorators.object
    def update_block(self, id: str, type_object: dict = None, archived: bool = None):
        url = f'{self.URL_PREFIX}blocks/{id}'
        data = {}
        if type_object:
            data.update(type_object)
        if archived is not None:
            data.update({
                'archived': archived
            })

        return requests.patch(url, headers=self.headers, json=data)

    @ResponseDecorators.object
    def delete_block(self, id: str):
        url = f'{self.URL_PREFIX}blocks/{id}'
        return requests.delete(url, headers=self.headers)

    @ResponseDecorators.pagination
    def get_block_children(self, id: str, start_cursor: str = None, page_size: int = None):
        url = f'{self.URL_PREFIX}blocks/{id}/children'
        params = {}
        if start_cursor:
            params['start_cursor'] = start_cursor
        if page_size:
            params['page_size'] = page_size

        return requests.get(url, headers=self.headers, params=params)

    @ResponseDecorators.object
    def append_block_children(self, id: str, children: List[dict]):
        url = f'{self.URL_PREFIX}blocks/{id}/children'
        data = {
            'children': children
        }
        return requests.patch(url, headers=self.headers, json=data)
