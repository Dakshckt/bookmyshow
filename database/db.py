
from pymongo import MongoClient
from django.conf import settings

try:
    client = MongoClient(
        settings.MONGO_DB["HOST"],
        serverSelectionTimeoutMS=5000
    )

    client.admin.command("ping")

    db = client[settings.MONGO_DB["DATABASE"]]

    print("MongoDB Atlas Connected Successfully!")

except Exception as err:
    print("Database Connection Error:", err)
    raise
