import os

from dotenv import load_dotenv

load_dotenv()

PUBLIC_BOT_TOKEN= os.getenv('PUBLIC_BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
ADMIN_USERS_IDS = os.getenv('ADMIN_USERS_IDS')
ADMINE_BOT_TOKEN= os.getenv('ADMINE_BOT_TOKEN')

BASE_LINK = os.getenv("BASE_LINK")
PUBLIC_BOT_LINK =os.getenv("PUBLIC_BOT_LINK")
NOTIFICATION_LINK = os.getenv("NOTIFICATION_LINK")
PRODAMUS_SECRET = os.getenv("SECRET_KEY")

DATABASE_URL = os.getenv("DATABASE_URL")