import csv
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")
collection_name = os.getenv("COLLECTION_NAME")

client = MongoClient(mongo_uri)
db = client[db_name]
collection = db[collection_name]

csv_file_path = "products.csv"

products = []

with open(csv_file_path, mode="r", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)

    print("CSV columns found:", reader.fieldnames)

    for row in reader:
        try:
            product = {
                "ProductID": int(row["ProductID"]),
                "Name": str(row["Name"]).strip(),
                "UnitPrice": float(row["UnitPrice"]),
                "StockQuantity": int(row["StockQuantity"]),
                "Description": str(row["Description"]).strip()
            }
            products.append(product)
        except Exception as e:
            print("Skipping bad row:", row)
            print("Reason:", e)

if products:
    collection.delete_many({}) 
    collection.insert_many(products)
    print(f"{len(products)} products inserted successfully into MongoDB.")
else:
    print("No products were inserted.")