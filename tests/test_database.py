
import unittest
import os
from src.notiondb import NotionDatabase, NotionModel
from src.notiondb.fields import *
from src.notiondb.block import *
from .env import load_env

load_env()

skipTests = False


class TestNotionModel(NotionModel):
  
    def __init__(self, database=None, id=None):
        super().__init__(database=database, id=id)

        self.name = TitleField('Name')
        self.description = RichTextField('Description')
        self.in_stock = CheckboxField('In stock')
        self.food_group = SelectField('Food group')
        self.price = NumberField('Price')


class TestDatabase(unittest.TestCase):

    TOKEN = os.environ.get('NOTION_TOKEN')
    
    DEV_PAGE_NOTION_ID = os.environ.get('DEV_PAGE_NOTION_ID')
    
    @unittest.skipIf(skipTests, '...')
    def test_db_a_create_database(self):
        props = [
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
            DateField(name='Last ordered'),
            LastEditedTimeField('Last edited time'),
        ]
        database = NotionDatabase(self.TOKEN, parent_id=self.DEV_PAGE_NOTION_ID, title='Test database', properties=props)
        info = database.info()
        TestDatabase.database = database
        self.assertEqual(info.get('title'), 'Test database')

    @unittest.skipIf(skipTests, '...')
    def test_db_b_update_database(self):
        info = self.database.update_database('Test database updated title')
        self.assertEqual(info.get('title'), 'Test database updated title')

    @unittest.skipIf(skipTests, '...')
    def test_db_c_insert_one(self):
        props: List[BaseField] = [
            TitleField('Name', "Tuscan Kale"),
            RichTextField('Description', "A dark green leafy vegetable"),
            SelectField('Food group', "🥦Vegetable"),
            NumberField('Price', 2.5),
        ]
        props_obj = {}
        for prop in props:
            prop.value = prop.default
            props_obj.update(prop.update_prop)

        children: List[BaseBlock] = [
            HeadingTwoBlock("Lacinato kale"),
            ParagraphBlock("Lacinato kale is a variety of kale with a long tradition in Italian cuisine, especially that of Tuscany. It is also known as Tuscan kale, Italian kale, dinosaur kale, kale, flat back kale, palm tree kale, or black Tuscan palm.", link="https://en.wikipedia.org/wiki/Lacinato_kale"),
        ]
        children = [child.value for child in children]

        item = self.database.insert_one(properties=props_obj, children=children)
        TestDatabase.page_id = item.get('_id')
        self.assertIsNotNone(item)

    @unittest.skipIf(skipTests, '...')
    def test_db_d_update_one(self):
        props: List[BaseField] = [
            TitleField('Name', "Tuscan Kale updated"),
        ]
        props_obj = {}
        for prop in props:
            prop.value = prop.default
            props_obj.update(prop.update_prop)
        
        response = self.database.update_one(self.page_id, properties=props_obj)
        self.assertIsNotNone(response)

    @unittest.skipIf(skipTests, '...')
    def test_db_e_delete_one(self):
        item = self.database.delete_one(self.page_id)
        self.assertTrue(item.get('_archived'))

    @unittest.skipIf(skipTests, '...')
    def test_db_e_delete_many(self):
        item_ids = []
        item_count = 5

        for i in range(item_count):
            props: List[BaseField] = [
                TitleField('Name', f"Tuscan Kale {i}"),
                RichTextField('Description', "A dark green leafy vegetable"),
                SelectField('Food group', "🥦Vegetable"),
                NumberField('Price', 2.5),
            ]
            props_obj = {}
            for prop in props:
                prop.value = prop.default
                props_obj.update(prop.update_prop)

            item = self.database.insert_one(properties=props_obj)

            item_ids.append(item.get('_id'))
        
        result = self.database.delete_many(ids=item_ids)
        self.assertEqual(len([item for item in result if item.get('_archived')]), item_count)

    # Test NotionModel

    @unittest.skipIf(skipTests, '...')
    def test_model_a_create_model(self):
        model = TestNotionModel(self.database)

        model.name.value = 'Name 1'
        model.description.value = 'Description 1'
        model.in_stock.value = True
        model.food_group.value = '🥦Vegetable'
        model.price.value = 2.33

        response = model.save()

        TestDatabase.model_id = model.id

        self.assertIsNotNone(response)

    @unittest.skipIf(skipTests, '...')
    def test_model_b_update_model(self):
        model = TestNotionModel.from_id(self.database, self.model_id)

        model.name.value = 'Name 2 updated'

        response = model.save()

        self.assertIsNotNone(response)

    @unittest.skipIf(skipTests, '...')
    def test_model_c_append_children(self):
        model = TestNotionModel.from_id(self.database, self.model_id)

        children = [
            TableOfContentsBlock(),
            BreadcrumbBlock(),
            DividerBlock(),
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
            EmbedBlock('https://codepen.io/hexagoncircle/pen/XWbWKwL'),
            BookmarkBlock('https://developers.notion.com/reference/block'),
            FileBlock('https://raw.githubusercontent.com/trimstray/the-book-of-secret-knowledge/master/README.md'),
            ImageBlock('https://i.pinimg.com/236x/4c/f6/c4/4cf6c4c4803969654cbc1076f98db539.jpg'),
            VideoBlock('https://www.youtube.com/watch?v=RQ9_TKayu9s'),
            PdfBlock('http://www.africau.edu/images/default/sample.pdf'),
            DividerBlock(),
            EquationBlock('e=mc^2'),
            # ChildPageBlock('Child page'),
            # ChildDatabaseBlock('Child database'),
            CodeBlock('console.log("Hello World!")', 'javascript'),
        ]

        response = model.append_children(children)

        self.assertIsNotNone(response)

        model_children = model.to_json(includes_children=True).get('children')

        self.assertEqual(len(model_children), len(children))

    @unittest.skipIf(skipTests, '...')
    def test_model_c_append_children_pagination(self):
        model = TestNotionModel.from_id(self.database, self.model_id)
        children = []
        for i in range(300):
            children.append(ParagraphBlock(f'paragraph {i}'))
        response = model.append_children(children)

        self.assertIsNotNone(response)

        model_children = model.to_json(includes_children=True).get('children')

        self.assertGreater(len(model_children), len(children))

    @unittest.skipIf(skipTests, '...')
    def test_model_d_get_children(self):
        model = TestNotionModel.from_id(self.database, self.model_id)

        children = model.get_children()

        self.assertGreater(len(children), 300)

    @unittest.skipIf(skipTests, '...')
    def test_model_d_query_model(self):
        cursor = TestNotionModel.objects(self.database).get()
        result = []
        for item in cursor:
            result.append(item)

        self.assertGreater(len(result), 0)

    @unittest.skipIf(skipTests, '...')
    def test_model_f_delete_model(self):
        self.test_model_a_create_model()
        model = TestNotionModel.from_id(self.database, self.model_id)

        response = model.delete()

        self.assertIsNotNone(response)
