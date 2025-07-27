import os

from dotenv import load_dotenv

load_dotenv()

PUBLIC_BOT_TOKEN= os.getenv('PUBLIC_BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

BASE_LINK = os.getenv("BASE_LINK")
PUBLIC_BOT_LINK =os.getenv("PUBLIC_BOT_LINK")
NOTIFICATION_LINK = os.getenv("NOTIFICATION_LINK")

DATABASE_URL = os.getenv("DATABASE_URL")