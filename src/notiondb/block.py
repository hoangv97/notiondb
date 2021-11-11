
from typing import List


class BaseBlock(object):

    block_type = ''

    properties = []

    def __init__(self, value: str = None, link: str = None, children = None):
        self._value = value
        self._link = link
        self._children: List[BaseBlock] = children or []

    def text(self):
        return [
            {
                'type': 'text',
                'text': {
                    'content': self._value,
                    'link': None if not self._link else {'url': self._link},
                }
            }
        ]

    def children(self):
        return [child.value for child in self._children]

    @property
    def value(self):
        return {
            'type': self.block_type,
            self.block_type: {
                prop: getattr(self, prop)() for prop in self.properties
            },
        }

    @value.setter
    def value(self, value):
        self._value = value

    @value.deleter
    def value(self):
        self._value = None


class ParagraphBlock(BaseBlock):

    block_type = 'paragraph'

    properties = ['text', 'children']


class HeadingOneBlock(BaseBlock):

    block_type = 'heading_1'

    properties = ['text']


class HeadingTwoBlock(HeadingOneBlock):

    block_type = 'heading_2'


class HeadingThreeBlock(HeadingOneBlock):
  
    block_type = 'heading_3'


class BulletedListItemBlock(BaseBlock):

    block_type = 'bulleted_list_item'

    properties = ['text', 'children']


class NumberedListItemBlock(BaseBlock):
  
    block_type = 'numbered_list_item'

    properties = ['text', 'children']


class ToDoBlock(BaseBlock):
  
    block_type = 'to_do'

    properties = ['text', 'children']


class ToggleBlock(BaseBlock):
  
    block_type = 'toggle'

    properties = ['text', 'children']


class CodeBlock(BaseBlock):

    def __init__(self, value: str, language: str = None):
        super().__init__(value=value)
        self._language = language

    block_type = 'code'
    
    properties = ['text', 'language']

    def language(self):
        return self._language


class ColumnBlock(BaseBlock):
  
    def __init__(self, blocks: List[BaseBlock]):
        super().__init__(value=None)
        self._children = blocks

    block_type = 'column'
    
    properties = ['children']

    def children(self):
        return [block.value for block in self._children]


class ColumnListBlock(ColumnBlock):
  
    def __init__(self, columns: List[ColumnBlock]):
        super().__init__(blocks=columns)

    block_type = 'column_list'


class ChildPageBlock(BaseBlock):
  
    block_type = 'child_page'

    properties = ['title']

    def title(self):
        return self._value


class ChildDatabaseBlock(ChildPageBlock):
  
    block_type = 'child_database'


class EmbedBlock(BaseBlock):
  
    block_type = 'embed'

    properties = ['url']

    def url(self):
        return self._value


class BookmarkBlock(EmbedBlock):
  
    block_type = 'bookmark'


class FileBlock(BaseBlock):

    block_type = 'file'

    properties = ['type', 'external']

    def type(self):
        return 'external'

    def external(self):
        return {
            'url': self._value
        }

class ImageBlock(FileBlock):

    block_type = 'image'


class VideoBlock(FileBlock):
  
    block_type = 'video'


class PdfBlock(FileBlock):

    block_type = 'pdf'


class EquationBlock(BaseBlock):
  
    block_type = 'equation'

    properties = ['expression']

    def expression(self):
        return self._value  # A KaTeX compatible string


class DividerBlock(BaseBlock):

    block_type = 'divider'


class TableOfContentsBlock(BaseBlock):
  
    block_type = 'table_of_contents'


class BreadcrumbBlock(BaseBlock):
  
    block_type = 'breadcrumb'
