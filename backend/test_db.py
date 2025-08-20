import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL", ""))
conn = engine.connect()
print("Connected:", conn.closed == False)
conn.close()
