
from .consts import *
from datetime import datetime
import traceback


class BlockParser(object):

    paragraph_tag_wrapper = 'p'  # default

    def __init__(self, data):
        self.data = data

        self.type = self.data.get('type')
        self._value = self.data[self.type]

    def get_color_style(self, color):
        if not color or color not in COLORS_DICT:
            return None
        if 'background' in color:
            return f'background: {COLORS_DICT[color]}'
        else:
            return f'color: {COLORS_DICT[color]}'

    def parse_text(self, text):
        try:
            result = ''
            content = text['text']['content']
            
            link = text['text']['link']

            styles = []
            annotations = text['annotations']
            if annotations.get('bold'):
                styles.append('font-weight: bold')
            if annotations.get('italic'):
                styles.append('font-style: italic')
            if annotations.get('strikethrough'):
                styles.append('text-decoration: line-through')
            if annotations.get('underline'):
                styles.append('text-decoration: underline')
            
            color_style = self.get_color_style(annotations.get('color'))
            if color_style:
                styles.append(color_style)

            style = '; '.join(styles)
            style = f'"{style}"'

            if link:
                url = link['url']
                result = f'<a href="{url}" target="_blank"{f" style={style}" if styles else ""}>{content}</a>'
            else:
                result = f'<span style={style}>{content}</span>' if styles else content

            return result
        except Exception as e:
            traceback.print_exc()
            return ''

    def rich_text(self):
        return ''.join([line.get('plain_text', '') for line in self._value])

    def text(self):
        return self.rich_text()

    def title(self):
        return self.rich_text()

    def number(self):
        return self._value

    def checkbox(self):
        return self._value

    def date(self):
        return self._value

    def url(self):
        return self._value

    def select(self):
        if self._value:
            self._value['background'] = COLORS_DICT.get(self._value.get('color', '') + '_background')
        return self._value

    def multi_select(self):
        if not self._value:
            return []
        result = []
        for item in self._value:
            item['background'] = COLORS_DICT.get(item.get('color', '') + '_background')
            result.append(item)
        return result

    def paragraph(self):
        text = ''.join([self.parse_text(text) for text in self._value.get('text', [])])
        return f'<{self.paragraph_tag_wrapper}>{text}</{self.paragraph_tag_wrapper}>'

    def to_do(self):
        text = ''.join([self.parse_text(text) for text in self._value.get('text', [])])
        checked = ' checked' if self._value.get('checked', False) else ''
        return f'<{self.paragraph_tag_wrapper}><input type="checkbox"{checked}>{text}</{self.paragraph_tag_wrapper}>'

    def bulleted_list_item(self):
        text = ''.join([self.parse_text(text) for text in self._value.get('text', [])])
        return f'<{self.paragraph_tag_wrapper}><li>{text}</li></{self.paragraph_tag_wrapper}>'

    def numbered_list_item(self):
        text = ''.join([self.parse_text(text) for text in self._value.get('text', [])])
        return f'<{self.paragraph_tag_wrapper}><li>{text}</li></{self.paragraph_tag_wrapper}>'

    def toggle(self):
        return self.paragraph()

    def heading_1(self):
        self.paragraph_tag_wrapper = 'h1'
        return self.paragraph()

    def heading_2(self):
        self.paragraph_tag_wrapper = 'h2'
        return self.paragraph()

    def heading_3(self):
        self.paragraph_tag_wrapper = 'h3'
        return self.paragraph()

    # Foreign key
    def relation(self):
        return [] if not self._value else [value.get('id') for value in self._value]

    def created_time(self):
        return datetime.strptime(self._value[:-2], '%Y-%m-%dT%H:%M:%S.%f')

    def last_edited_time(self):
        return self.created_time()

    def image(self):
        file_type = self._value.get('type', '')
        url = self._value.get(file_type, {}).get('url')
        
        caption = self._value.get('caption', [])
        if caption and caption[0]:
            caption = self.parse_text(caption[0])
        
        return f'<img src="{url}" alt="{caption}">'

    def embed(self):
        url = self._value.get('url')

        return f'<a href="{url}">{url}</a>'

    def bookmark(self):
        return self.embed()

    def video(self):
        return self.file()

    def file(self):
        file_type = self._value.get('type', '')
        url = self._value.get(file_type, {}).get('url')

        return f'<a href="{url}">{url}</a>'

    def pdf(self):
        return self.file()

    def unsupported(self):
        return None
    
    @property
    def value(self):
        try:
            return getattr(self, self.type)()
        except Exception as e:
            return None
