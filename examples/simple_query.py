# examples/simple_query.py

from pydantic_sql.adapter import PydanticSQL
from models import User, Product, Order, Category
from typing import List
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

# Connection parameters
connection_params = {
    "host": os.getenv("TEST_DB_HOST"),
    "database": os.getenv("TEST_DB_NAME"),
    "user": os.getenv("TEST_DB_USER"),
    "password": os.getenv("TEST_DB_PASSWORD")
}

# Initialize the PydanticSQL adapter
db = PydanticSQL(connection_params)

async def showcase_pydanticsql():
    print("PydanticSQL Usage Examples")
    print("==========================")

    # Example 1: Simple query with model mapping
    print("\n1. Fetching a user by ID:")
    query = "SELECT * FROM users WHERE id = :user_id"
    user = await db.fetch_one(query, {"user_id": 1}, model=User)
    print(f"User: {user}")

    # Example 2: Fetching multiple rows
    print("\n2. Fetching all products:")
    query = "SELECT * FROM products"
    products = await db.fetch(query, model=Product)
    for product in products:
        print(f"Product: {product.name}, Price: {product.price}")

    # Example 3: Inserting data
    print("\n3. Creating a new category:")
    query = "INSERT INTO categories (name, description) VALUES (:name, :description) RETURNING *"
    params = {"name": "New Category", "description": "A brand new category"}
    new_category = await db.fetch_one(query, params, model=Category)
    print(f"New category created: {new_category}")

    # Example 4: Updating data
    print("\n4. Updating a product's price:")
    query = "UPDATE products SET price = :new_price WHERE id = :product_id RETURNING *"
    params = {"new_price": 999.99, "product_id": 1}
    updated_product = await db.fetch_one(query, params, model=Product)
    print(f"Updated product: {updated_product}")

    # Example 5: Deleting data
    print("\n5. Deleting a category:")
    query = "DELETE FROM categories WHERE id = :category_id RETURNING id"
    result = await db.fetch_one(query, {"category_id": new_category.id})
    print(f"Deleted category with ID: {result['id']}")

    # Example 6: Transaction example
    print("\n6. Creating an order (transaction example):")
    async with db.transaction():
        # First, get the product details
        product_query = "SELECT * FROM products WHERE id = :product_id"
        product = await db.fetch_one(product_query, {"product_id": 1}, model=Product)
        
        # Then, create the order
        order_query = """
        INSERT INTO orders (user_id, product_id, quantity, total_price)
        VALUES (:user_id, :product_id, :quantity, :total_price)
        RETURNING *
        """
        order_params = {
            "user_id": 1,
            "product_id": product.id,
            "quantity": 2,
            "total_price": product.price * 2
        }
        new_order = await db.fetch_one(order_query, order_params, model=Order)
        print(f"New order created: {new_order}")

    # Example 7: Complex query with joins
    print("\n7. Fetching orders with user and product details:")
    query = """
    SELECT o.*, u.name as user_name, p.name as product_name
    FROM orders o
    JOIN users u ON o.user_id = u.id
    JOIN products p ON o.product_id = p.id
    LIMIT 5
    """
    results = await db.fetch(query)
    for row in results:
        print(f"Order ID: {row['id']}, User: {row['user_name']}, Product: {row['product_name']}")

async def main():
    await showcase_pydanticsql()

if __name__ == "__main__":
    asyncio.run(main())