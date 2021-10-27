from os.path import join, dirname
from dotenv import load_dotenv


def load_env():
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
