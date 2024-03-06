from fastapi import FastAPI
from enum import Enum

fastapp = FastAPI(
    title="Hello World",
)

@fastapp.get('/')
def get_root():
    return {"message": "Hello World"}

@fastapp.get("/retrive")
def get_retrive():
    return {"message": "Get Retrived!"}

@fastapp.get("/products/{product_id}")
def get_products(product_id: int):
    return {"message": f"Get Product {product_id}"}

class Product(str, Enum):
    product1 = "Mobile1",
    product2 = "Iphone",
    product3 = "Laptop",

@fastapp.get("/devices/{devices_name}")
def get_devices(device_name: Product):
    return {"Device_name" : f"You Like a {device_name.value}"}