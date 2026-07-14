import os
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DB_NAME   = os.getenv("DB_NAME", "port_konteyner")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db     = client[DB_NAME]

users_col      = db["users"]
containers_col = db["containers"]

# (first_name, last_name) çifti benzersiz olmalı
users_col.create_index(
    [("first_name", ASCENDING), ("last_name", ASCENDING)],
    unique=True,
)
