from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from decimal import Decimal

class User(BaseModel):
    """Represents a user in the system."""
    id: int = Field(..., description="User ID")
    name: str = Field(..., description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    age: Optional[int] = Field(None, description="User's age")
    created_at: datetime = Field(..., description="Timestamp of user creation")

class Category(BaseModel):
    """Represents a product category."""
    id: int = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")

class Product(BaseModel):
    """Represents a product in the inventory."""
    id: int = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: Decimal = Field(..., description="Product price", ge=0)
    stock: int = Field(..., description="Current stock quantity", ge=0)
    category_id: int = Field(..., description="ID of the product's category")
    created_at: datetime = Field(..., description="Timestamp of product creation")

class Order(BaseModel):
    """Represents an order in the system."""
    id: int = Field(..., description="Order ID")
    user_id: int = Field(..., description="ID of the user who placed the order")
    product_id: int = Field(..., description="ID of the ordered product")
    quantity: int = Field(..., description="Quantity of products ordered", gt=0)
    total_price: Decimal = Field(..., description="Total price of the order", ge=0)
    order_date: datetime = Field(..., description="Timestamp of the order")