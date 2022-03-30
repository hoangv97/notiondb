

class BaseField:

    type = None

    def __init__(self, name: str, default = None):
        self.name = name
        self.default = default
        self._value = default
        self._updated = False

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value is not None:
            self._updated = True
            self.set_value(value)
    
    def set_value(self, value):
        self._value = value

    @value.deleter
    def value(self):
        self._value = self.default

    @property
    def is_updated(self):
        return self._updated

    @property
    def update_prop(self):
        if self.value is None or not self.is_updated:
            return None
        return {
            self.name: {
                self.type: self.update_value
            }
        }

    @property
    def update_value(self):
        return self.value

    def query_filter(self, value):
        return {
            'property': self.name,
            self.type: value,
        }

    def get_creating_prop_config(self):
        return {}

    def get_creating_database_prop(self):
        return {
            self.name: {
                self.type: self.get_creating_prop_config()
            }
        }


# Primary key
class TitleField(BaseField):

    type = 'title'

    @property
    def update_value(self):
        return [
            {
                'text': {
                    'content': self.value
                }
            }
        ]


class RichTextField(TitleField):

    type = 'rich_text'


class NumberField(BaseField):

    type = 'number'

    def __init__(self, name, default=None, format=None):
        super().__init__(name, default=default)
        
        self.format = format

    def get_creating_prop_config(self):
        return {} if not self.format else {'format': self.format}


class CheckboxField(BaseField):

    type = 'checkbox'


class UrlField(BaseField):

    type = 'url'


class SelectField(BaseField):

    type = 'select'

    def __init__(self, name, default=None, options=None):
        super().__init__(name, default=default)
        
        self.options = options

    @property
    def update_value(self):
        return {
            'name': self.value
        }

    def get_creating_prop_config(self):
        return {} if not self.options else {'options': self.options}


class MultiSelectField(SelectField):

    type = 'multi_select'

    @property
    def update_value(self):
        return [{'name': value} for value in self.value]


class DateField(BaseField):

    type = 'date'


class CreatedTimeField(BaseField):

    type = 'created_time'

    @property
    def is_updated(self):
        return False


class LastEditedTimeField(CreatedTimeField):
  
    type = 'last_edited_time'


class RelationField(BaseField):

    type = 'relation'

    @property
    def update_value(self):
        return [{'id': value} for value in self.value]
