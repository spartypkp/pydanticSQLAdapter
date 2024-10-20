# examples/simple_query.py

import psycopg
from pydantic_sql.query import Query
from models import User, Product, Order, Category
from typing import List
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

def showcase_pydanticsql():
    print("PydanticSQL Usage Examples")
    print("==========================")

    # Create a database connection
    conn = psycopg.connect(**connection_params)

    # Example 1: Simple query with model mapping
    print("\n1. Fetching a user by ID:")
    query = Query("SELECT * FROM users WHERE name = {user_id}")
    user = query.run({"user_id": 1}, model=User, db_connection=conn)
    print(f"User: {user}")

    # Example 2: Fetching multiple rows
    print("\n2. Fetching all products:")
    query = Query("SELECT * FROM products")
    products = query.run(model=Product, db_connection=conn)
    for product in products:
        print(f"Product: {product.name}, Price: {product.price}")

    # Example 3: Inserting data
    print("\n3. Creating a new category:")
    query = Query("INSERT INTO categories (name, description) VALUES ({name}, {description}) RETURNING *")
    params = {"name": "New Category", "description": "A brand new category"}
    new_category = query.run(params, model=Category, db_connection=conn)
    print(f"New category created: {new_category}")

    # Example 4: Updating data
    print("\n4. Updating a product's price:")
    query = Query("UPDATE products SET price = {new_price} WHERE id = {product_id} RETURNING *")
    params = {"new_price": 999.99, "product_id": 1}
    updated_product = query.run(params, model=Product, db_connection=conn)
    print(f"Updated product: {updated_product}")

    # Example 5: Deleting data
    print("\n5. Deleting a category:")
    query = Query("DELETE FROM categories WHERE id = {category_id} RETURNING id")
    result = query.run({"category_id": new_category.id}, db_connection=conn)
    print(f"Deleted category with ID: {result['id']}")

    # Example 6: Transaction example
    print("\n6. Creating an order (transaction example):")
    try:
        with conn.cursor() as cur:
            # First, get the product details
            product_query = Query("SELECT * FROM products WHERE id = {product_id}")
            product = product_query.run({"product_id": 1}, model=Product, db_connection=conn)
            
            # Then, create the order
            order_query = Query("""
            INSERT INTO orders (user_id, product_id, quantity, total_price)
            VALUES ({user_id}, {product_id}, {quantity}, {total_price})
            RETURNING *
            """)
            order_params = {
                "user_id": 1,
                "product_id": product.id,
                "quantity": 2,
                "total_price": product.price * 2
            }
            new_order = order_query.run(order_params, model=Order, db_connection=conn)
            print(f"New order created: {new_order}")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error creating order: {e}")

    # Example 7: Complex query with joins
    print("\n7. Fetching orders with user and product details:")
    query = Query("""
    SELECT o.*, u.name as user_name, p.name as product_name
    FROM orders o
    JOIN users u ON o.user_id = u.id
    JOIN products p ON o.product_id = p.id
    LIMIT 5
    """)
    results = query.run(db_connection=conn)
    for row in results:
        print(f"Order ID: {row['id']}, User: {row['user_name']}, Product: {row['product_name']}")

    # Close the database connection
    conn.close()

def main():
    showcase_pydanticsql()

if __name__ == "__main__":
    main()