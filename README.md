# NotionDB

Python 3 tools for interacting with Notion API:

- API client

- Relational database wrapper

## Changelog

- 11/11: Add column list, column block

## Installation

`pip install notiondb`

## API client

```python
from notiondb import NotionApi

api = NotionApi(API_TOKEN)  # Token from Internal Integration

# Databases
databases, next_cursor = api.get_databases()

api.create_database(parent_id, title, properties)

api.get_database(id)

api.update_database(id, title, properties)

pages, next_cursor = api.query_database(filter, sorts, start_cursor, page_size)

# Pages
pages, next_cursor = api.get_pages(query, start_cursor, page_size)

# Create page in database
api.create_page('database_id', parent_id, title, properties, children, icon, cover)
# Create page in parent page
api.create_page('page_id', parent_id, title, properties, children, icon, cover)

api.get_page(id)

api.update_page(id, properties, archived)

# Get page's block children
blocks, next_cursor = api.get_block_children(id, start_cursor, page_size)

api.append_block_children(id, children)

```

## Wrapper for relational database

Interacting with Notion database as a relational database.

### Create database

```python
from notiondb import NotionDatabase
from notiondb.fields import *

properties = [
    TitleField(name='Name'),
    RichTextField(name='Description'),
    CheckboxField(name='In stock'),
    SelectField(name='Food group', options=[
        {
            "name": "🥦Vegetable",
            "color": "green"
        },
        {
            "name": "🍎Fruit",
            "color": "red"
        },
        {
            "name": "💪Protein",
            "color": "yellow"
        }
    ]),
    NumberField(name='Price', format='dollar'),
]

# Create new database
database = NotionDatabase(TOKEN, parent_id=NOTION_PARENT_PAGE_ID, title='Database title', properties=properties)

# Or get existing database
database = NotionDatabase(TOKEN, database_id=DATABASE_ID)
```

### Define document's structure

```python
from notiondb import NotionModel
from notiondb.fields import *


class TestModel(NotionModel):
  
    def __init__(self, database=None, id=None):
        super().__init__(database=database, id=id)

        self.name = TitleField('Name')
        self.description = RichTextField('Description')
        self.in_stock = CheckboxField('In stock')
        self.food_group = SelectField('Food group')
        self.price = NumberField('Price')

```

### Add a row

```python
model = TestModel(database)

model.name.value = 'Name'
model.description.value = 'Description'
model.in_stock.value = True
model.food_group.value = '🥦Vegetable'
model.price.value = 2.33

model.save()
```

### Update a row

```python
# Get a row from id
model = TestModel.from_id(database, row_id)
# Or from data retrieved by API
model = TestModel.from_data(database, data)

model.name.value = 'Name updated'

model.save()
```

### Append block children to page

```python
from notiondb.block import *

children = [
    TableOfContentsBlock(),
    ParagraphBlock('paragraph 1'),
    ParagraphBlock('paragraph 2', link='https://example.com'),
]
model.append_children(children)

```

### Query database

[Filter & sorts reference](https://developers.notion.com/reference/post-database-query#post-database-query-filter)

```python
cursor = TestModel.objects(database).get(filter=filter, sorts=sorts, limit=limit)
for item in cursor:
    # do something
```


### Get row's data

```python
# Get row's block children
children = model.get_children()

# Parse to JSON
data = model.to_json(includes_children=True)
```

### Delete a row

```python
model.delete()
```

## Testing

Create .env file in ./tests

```env
NOTION_TOKEN=
# Parent page id for testing
DEV_PAGE_NOTION_ID=
```

Run tests

`python -m unittest`
