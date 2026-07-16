import os
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DB_NAME   = os.getenv("DB_NAME", "port_konteyner")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]

users_col  = db["users"]
containers_col  = db["containers"]
revoked_tokens_col = db["revoked_tokens"]

containers_col.create_index([("container_no", ASCENDING)], unique=True)
containers_col.create_index([("container_id", ASCENDING)], unique=True, sparse=True)

# Logout edilen token'lar 8 saat sonra otomatik silinir (JWT süresiyle eşleşir)
revoked_tokens_col.create_index("revoked_at", expireAfterSeconds=8 * 3600)
