from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client = MongoClient(MONGODB_URL)
db = client[DATABASE_NAME]
companies_collection = db["companies"]

try:
    result = companies_collection.update_many(
        {},
        {
            "$set": {
                "investors.$[].action": None,
                "investors.$[].link": None,
                "financialStatement.$[].action": None,
                "financialStatement.$[].link": None,
                "assessment.$[].action": None,
                "assessment.$[].link": None,
                "portfolio.$[].action": None,
                "portfolio.$[].link": None,
                "transformation_plan.$[].action": None,
                "transformation_plan.$[].link": None,
                "dynamicSections.$[].value.$[].action": None,
                "dynamicSections.$[].value.$[].link": None,
            }
        },
    )

    print(f"Modified {result.modified_count} documents.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    client.close()