# PydanticSQL Adapter Project Plan

## Goal
Create a lightweight, type-safe SQL adapter for Python that allows writing pure SQL queries while leveraging Pydantic models for type safety and data validation.

## Description
PydanticSQL Adapter aims to provide a seamless interface between Python code and SQL databases. It will allow developers to write raw SQL queries with the added benefits of strong typing, automatic parameter handling, and result mapping to Pydantic models. This adapter will simplify database interactions while maintaining the flexibility and power of SQL, without the overhead of a full ORM.

## Core Features

1. **Raw SQL Query Execution**
   - Execute raw SQL queries with PostgreSQL-style parameter substitution ($1, $2, etc.)
   - Maintain full control over SQL syntax without abstractions (AS LITTLE AS POSSIBLE)

2. **Automatic Type Inference**
   - Infer result types directly from the database schema and query structure
   - Generate Pydantic models automatically based on inferred types
   - Heavily based on previous work by PGTyped https://github.com/adelsz/pgtyped

3. **Flexible Result Mapping**
   - Use auto-generated Pydantic models for query results
   - Allow optional user-defined Pydantic models to override or extend inferred types

4. **Type-safe Parameter Handling**
   - Use Pydantic models as parameter sources
   - Match parameters to PostgreSQL-style placeholders ($1, $2, etc.) automatically

5. **Database Schema Integration**
   - Utilize live database connection for real-time type information
   - Support for generating models from existing database tables and views

6. **Query Analysis and Validation**
   - Parse SQL queries to extract placeholders and validate syntax
   - Provide helpful error messages for mismatched types or invalid queries

7. **Development Workflow Tools**
   - Implement a watch mode for real-time model generation as queries are written
   - Provide utilities for managing and organizing SQL queries within a project

8. **Performance Optimization**
   - Efficient query execution using Psycopg3
   - Support for prepared statements and connection pooling

9. **Async Support**
   - Provide both synchronous and asynchronous interfaces for query execution

10. **SQL Injection Prevention**
    - Utilize parameterized queries to prevent SQL injection vulnerabilities
    - Send queries and parameters separately to the database driver for secure execution
## Extra Features

1. **Bulk Operations**
   - Support efficient bulk inserts and updates

2. **Lightweight Query Composition**
   - Allow simple query modifications without hiding the underlying SQL

3. **Automatic Model Generation**
   - Generate Pydantic models from database schema or query results

4. **Async Support**
   - Provide asynchronous query execution for compatibility with async frameworks

5. **Schema Validation**
   - Validate Pydantic models against database schema

6. **Raw SQL Execution with Type Checking**
   - Allow execution of complex raw SQL queries with result type checking


## Usage Examples

### Basic Query Execution
```python
from pydanticsql import PydanticSQL
from models import UserModel

# Simple select query
users = PydanticSQL("SELECT * FROM users WHERE age > :min_age",
                    params={"min_age": 18},
                    result_model=UserModel)e

# Iterate through strongly-typed results
for user in users:
    print(f"User {user.name} is {user.age} years old")
```

### Type-safe Parameter Passing
```python
from pydanticsql import PydanticSQL
from models import UserModel

new_user = UserModel(name="Alice", age=30, email="alice@example.com")

# Insert using Pydantic model as parameters
PydanticSQL("INSERT INTO users (name, age, email) VALUES (:name, :age, :email)",
            params=new_user)

# The adapter automatically extracts values from the Pydantic model
```

### Transaction Support
```python
from pydanticsql import PydanticSQL

with PydanticSQL.transaction():
    PydanticSQL("UPDATE accounts SET balance = balance - :amount WHERE id = :from_id",
                params={"amount": 100, "from_id": 1})
    PydanticSQL("UPDATE accounts SET balance = balance + :amount WHERE id = :to_id",
                params={"amount": 100, "to_id": 2})
    # If any query fails, the entire transaction is rolled back
```

### Bulk Operations
```python
from pydanticsql import PydanticSQL
from models import UserModel

new_users = [
    UserModel(name="Bob", age=25, email="bob@example.com"),
    UserModel(name="Charlie", age=35, email="charlie@example.com"),
    UserModel(name="David", age=28, email="david@example.com")
]

PydanticSQL("INSERT INTO users (name, age, email) VALUES (:name, :age, :email)",
            params=new_users,
            bulk=True)
```

### Async Support
```python
from pydanticsql import PydanticSQL
from models import UserModel

async def get_users():
    users = await PydanticSQL.async_("SELECT * FROM users WHERE age > :min_age",
                                     params={"min_age": 18},
                                     result_model=UserModel)
    return users

# In an async context
users = await get_users()
```

### Automatic Model Generation
```python
from pydanticsql import PydanticSQL

# Generate a Pydantic model based on a table schema
UserModel = PydanticSQL.generate_model("users")

# Use the generated model
users = PydanticSQL("SELECT * FROM users", result_model=UserModel)
```