import os
from dotenv import load_dotenv

load_dotenv()

""" Environment variables. """
TOKEN = os.getenv('DISCORD_TOKEN')
CACHEDIR = os.getenv('SPAWNINGTOOL_CACHE_DIR')

""" Other variables """
PROJ_DIR = os.path.dirname(__file__)
ENV_PATH = os.path.join(PROJ_DIR, '.env')
UPLOAD_DIR = os.path.join(PROJ_DIR, 'UPLOAD_DIR')
TEMP_ENV_PATH = os.path.join(PROJ_DIR, 'template.env')
SC2EXT = '.SC2Replay'
DISCORD_CHAR_LIMIT = 2000
