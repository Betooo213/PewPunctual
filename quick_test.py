from dotenv import load_dotenv
load_dotenv()                      # reads .env
import os, datetime as dt
print("Your Notion key is:", os.getenv("NOTION_KEY"))
print("Current UTC time:", dt.datetime.utcnow())
