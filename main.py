from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import certifi
import os
import requests

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")
collection_name = os.getenv("COLLECTION_NAME")

client = None
db = None
collection = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db, collection
    try:
        client = MongoClient(
            mongo_uri,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000
        )
        client.admin.command("ping")
        db = client[db_name]
        collection = db[collection_name]
        print("MongoDB Atlas connection successful")
    except Exception as e:
        print("MongoDB Atlas connection failed:", e)
        client = None
        db = None
        collection = None
    yield
    if client is not None:
        client.close()


app = FastAPI(title="Inventory Management API", lifespan=lifespan)


class ProductModel(BaseModel):
    ProductID: int = Field(..., gt=0)
    Name: str = Field(..., min_length=1)
    UnitPrice: float = Field(..., gt=0)
    StockQuantity: int = Field(..., ge=0)
    Description: str = Field(..., min_length=1)


def ensure_collection():
    if collection is None:
        raise HTTPException(status_code=503, detail="Database connection is not available")
    return collection


def product_serializer(product) -> dict:
    return {
        "ProductID": int(product["ProductID"]),
        "Name": str(product["Name"]),
        "UnitPrice": float(product["UnitPrice"]),
        "StockQuantity": int(product["StockQuantity"]),
        "Description": str(product["Description"])
    }


@app.get("/")
def root():
    return {"message": "Inventory Management API is running"}


@app.get("/getAll")
def get_all_products():
    coll = ensure_collection()
    try:
        products = list(coll.find({}, {"_id": 0}))
        return [product_serializer(product) for product in products]
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")


@app.get("/getSingleProduct")
def get_single_product(product_id: int = Query(..., gt=0)):
    coll = ensure_collection()
    try:
        product = coll.find_one({"ProductID": product_id}, {"_id": 0})

        if not product:
            product = coll.find_one({"ProductID": str(product_id)}, {"_id": 0})

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return product_serializer(product)
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")


@app.post("/addNew")
def add_new_product(product: ProductModel):
    coll = ensure_collection()

    existing_product = coll.find_one({"ProductID": product.ProductID}, {"_id": 0})
    if existing_product:
        raise HTTPException(status_code=400, detail="ProductID already exists")

    try:
        product_data = product.model_dump()
    except AttributeError:
        product_data = product.dict()

    coll.insert_one(product_data)

    safe_response = {
        "message": "Product added successfully",
        "product": {
            "ProductID": product_data["ProductID"],
            "Name": product_data["Name"],
            "UnitPrice": product_data["UnitPrice"],
            "StockQuantity": product_data["StockQuantity"],
            "Description": product_data["Description"]
        }
    }

    return safe_response

@app.delete("/deleteOne")
def delete_one_product(product_id: int = Query(..., gt=0)):
    coll = ensure_collection()
    try:
        result = coll.delete_one({"ProductID": product_id})

        if result.deleted_count == 0:
            result = coll.delete_one({"ProductID": str(product_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")

        return {"message": f"Product with ProductID {product_id} deleted successfully"}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database delete failed: {str(e)}")


@app.get("/startsWith")
def starts_with(letter: str = Query(..., min_length=1, max_length=1)):
    coll = ensure_collection()
    try:
        products = coll.find(
            {"Name": {"$regex": f"^{letter}", "$options": "i"}},
            {"_id": 0}
        )
        return [product_serializer(product) for product in products]
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")


@app.get("/paginate")
def paginate(start_id: int = Query(..., gt=0), end_id: int = Query(..., gt=0)):
    coll = ensure_collection()

    if start_id > end_id:
        raise HTTPException(status_code=400, detail="start_id must be less than or equal to end_id")

    try:
        products = coll.find(
            {"ProductID": {"$gte": start_id, "$lte": end_id}},
            {"_id": 0}
        ).sort("ProductID", 1).limit(10)

        return [product_serializer(product) for product in products]
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")


@app.get("/convert")
def convert_price(product_id: int = Query(..., gt=0)):
    coll = ensure_collection()

    try:
        product = coll.find_one({"ProductID": product_id}, {"_id": 0})

        if not product:
            product = coll.find_one({"ProductID": str(product_id)}, {"_id": 0})

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        unit_price_usd = float(product["UnitPrice"])

        response = requests.get(
            "https://api.frankfurter.dev/v1/latest",
            params={
                "base": "USD",
                "symbols": "EUR"
            },
            timeout=10
        )

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Exchange rate API request failed")

        data = response.json()

        if "rates" not in data or "EUR" not in data["rates"]:
            raise HTTPException(status_code=500, detail="Invalid exchange rate API response")

        exchange_rate = float(data["rates"]["EUR"])
        converted_price_eur = round(unit_price_usd * exchange_rate, 2)

        return {
            "ProductID": product["ProductID"],
            "Name": product["Name"],
            "UnitPriceUSD": unit_price_usd,
            "ExchangeRateUSDtoEUR": exchange_rate,
            "UnitPriceEUR": converted_price_eur
        }

    except HTTPException:
        raise
    except Exception as e:
        print("convert error:", e)
        raise HTTPException(status_code=500, detail=f"convert failed: {str(e)}")