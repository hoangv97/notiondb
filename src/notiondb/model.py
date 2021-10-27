
from .fields import BaseField
from .query_set import QuerySet
from .database import NotionDatabase
from .block import BaseBlock
from typing import List


class NotionModel:

    def __init__(self, database: NotionDatabase = None, id: str = None):
        self.database = database
        self.id = id

    @classmethod
    def objects(cls, database: NotionDatabase):
        return QuerySet(cls, database)

    @property
    def fields(self):
        attrs = dir(self)
        attrs = filter(lambda attr: '__' not in attr and attr not in ['fields'], attrs)
        attrs = filter(lambda attr: isinstance(getattr(self, attr), BaseField), attrs)
        fields: List[BaseField] = [getattr(self, attr) for attr in attrs]
        return fields

    @classmethod
    def from_id(cls, database: NotionDatabase, id: str):
        data = database.find_one(id)
        model = cls(database, id)
        for field in model.fields:
            if field.name in data:
                field.set_value(data[field.name])
        return model

    @classmethod
    def from_data(cls, database: NotionDatabase, data: dict):
        id = data.get('_id')
        model = cls(database, id)
        for field in model.fields:
            if field.name in data:
                field.set_value(data[field.name])
        return model

    def get_children(self):
        if not self.id:
            return None
        return self.database.get_children(self.id)

    def append_children(self, blocks: List[BaseBlock]):
        return self.database.append_children(self.id, blocks=blocks)

    def to_json(self, includes_children=False):
        if not self.id:
            return None
        
        data = {
            'id': self.id,
        }

        if includes_children:
            data.update({
                'children': self.get_children(),
            })

        for field in self.fields:
            data[field.name] = field.value
        return data

    def save(self):
        props = {}
        for field in self.fields:
            update_prop = field.update_prop
            if update_prop is not None:
                props.update(update_prop)

        if props == {}:
            return None

        # create new 
        if not self.id:
            response = self.database.insert_one(props)

            self.id = response['_id']
        # update
        else:
            response = self.database.update_one(self.id, props)

        # Reset updated status
        for field in self.fields:
            field._updated = False
        
        return response

    def delete(self):
        response = self.database.delete_one(self.id)
        return response
