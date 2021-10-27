
import unittest
import os
from src.notiondb import NotionApi
from src.notiondb.block import *
from .env import load_env

load_env()


skipTests = False


class TestApi(unittest.TestCase):

    TOKEN = os.environ.get('NOTION_TOKEN')
    
    DEV_PAGE_NOTION_ID = os.environ.get('DEV_PAGE_NOTION_ID')
    
    api = NotionApi(TOKEN)

    @unittest.skipIf(skipTests, '...')
    def test_api_a_get_all_databases(self):
        response, _ = self.api.get_databases()
        self.assertGreater(len(response), 0)

    @unittest.skipIf(skipTests, '...')
    def test_api_a_get_query_databases(self):
        response, _ = self.api.get_databases(query='IT', page_size=10)
        self.assertEqual(len(response), 1)

    @unittest.skipIf(skipTests, '...')
    def test_api_a_create_database(self):
        props = {
            "Name": {
                "title": {}
            },
            "Description": {
                "rich_text": {}
            },
            "In stock": {
                "checkbox": {}
            },
            "Food group": {
                "select": {
                    "options": [
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
                    ]
                }
            },
            "Price": {
                "number": {
                    "format": "dollar"
                }
            },
            "Last ordered": {
                "date": {}
            },
            "Check": {
                "rich_text": {}
            },
        }
        response = self.api.create_database(self.DEV_PAGE_NOTION_ID, title='Test api', properties=props)
        TestApi.database_id = response.get('id')
        self.assertIsNotNone(response)

    @unittest.skipIf(skipTests, '...')
    def test_api_b_get_database(self):
        response = self.api.get_database(self.database_id)
        self.assertEqual(response.get('id'), self.database_id)
    
    @unittest.skipIf(skipTests, '...')
    def test_api_c_update_database(self):
        props = {
            "Check": {
                "checkbox": {}
            },
        }
        response = self.api.update_database(self.database_id, title='Test api updated title', properties=props)
        self.assertIsNotNone(response)

    @unittest.skipIf(skipTests, '...')
    def test_api_d_create_page_in_database(self):
        props = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": "Tuscan Kale"
                        }
                    }
                ]
            },
            "Description": {
                "rich_text": [
                    {
                        "text": {
                            "content": "A dark green leafy vegetable"
                        }
                    }
                ]
            },
            "Food group": {
                "select": {
                    "name": "Vegetable"
                }
            },
            "Price": { "number": 2.5 }
        }
        children = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "text": [{ "type": "text", "text": { "content": "Lacinato kale" } }]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Lacinato kale is a variety of kale with a long tradition in Italian cuisine, especially that of Tuscany. It is also known as Tuscan kale, Italian kale, dinosaur kale, kale, flat back kale, palm tree kale, or black Tuscan palm.",
                                "link": { "url": "https://en.wikipedia.org/wiki/Lacinato_kale" }
                            }
                        }
                    ]
                }
            }
        ]
        response = self.api.create_page('database_id', self.database_id, properties=props, children=children)
        TestApi.page_id = response.get('id')
        self.assertIsNotNone(response)

    @unittest.skipIf(skipTests, '...')
    def test_api_e_update_page(self):
        props = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": "updated Tuscan Kale"
                        }
                    }
                ]
            },
        }
        response = self.api.update_page(self.page_id, properties=props)
        self.assertIsNotNone(response)

    @unittest.skipIf(skipTests, '...')
    def test_api_f_append_block_children(self):
        append_blocks = [
            ParagraphBlock('paragraph 1'),
            ParagraphBlock('paragraph 2', link='https://developers.notion.com/reference/block'),
            HeadingOneBlock('heading 1'),
            HeadingTwoBlock('heading 2'),
            HeadingThreeBlock('heading 3'),
            BulletedListItemBlock('bullet 1'),
            BulletedListItemBlock('bullet 2'),
            NumberedListItemBlock('number 1'),
            NumberedListItemBlock('number 2'),
            NumberedListItemBlock('number 3'),
            ToDoBlock('todo 1'),
            ToDoBlock('todo 2'),
            ToggleBlock('toggle 1', children=[
                HeadingOneBlock('toggle heading 1'),
                ParagraphBlock('toggle paragraph', link='https://developers.notion.com/reference/block'),
            ]),
        ]
        children = [block.value for block in append_blocks]
        response = self.api.append_block_children(self.page_id, children)
        self.assertIsNotNone(response)

    @unittest.skipIf(skipTests, '...')
    def test_api_h_delete_page(self):
        self.test_api_d_create_page_in_database()
        response = self.api.update_page(self.page_id, archived=True)
        self.assertTrue(response.get('archived'))

    @unittest.skipIf(skipTests, '...')
    def test_api_i_create_page_in_page(self):
        append_blocks = [
            ParagraphBlock('paragraph 1'),
            ParagraphBlock('paragraph 2', link='https://developers.notion.com/reference/block'),
            HeadingOneBlock('heading 1'),
            HeadingTwoBlock('heading 2'),
            HeadingThreeBlock('heading 3'),
            BulletedListItemBlock('bullet 1'),
            BulletedListItemBlock('bullet 2'),
            NumberedListItemBlock('number 1'),
            NumberedListItemBlock('number 2'),
            NumberedListItemBlock('number 3'),
            ToDoBlock('todo 1'),
            ToDoBlock('todo 2'),
            ToggleBlock('toggle 1', children=[
                HeadingOneBlock('toggle heading 1'),
                ParagraphBlock('toggle paragraph', link='https://developers.notion.com/reference/block'),
            ]),
        ]
        children = [block.value for block in append_blocks]
        response = self.api.create_page('page_id', self.DEV_PAGE_NOTION_ID, title='Test create page in page', children=children, icon='💪', cover='https://images.unsplash.com/photo-1632509323255-c0aac7791029?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&ixlib=rb-1.2.1&auto=format&fit=crop&w=870&q=80')
        self.assertIsNotNone(response)
