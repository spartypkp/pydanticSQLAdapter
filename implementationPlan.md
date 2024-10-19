# Expanded Implementation Plan

## 1. Research Phase

### 1.1 Existing Solutions
- Research existing SQL adapters, query builders, and ORMs
- Analyze their strengths and weaknesses
- Identify gaps that PydanticSQL Adapter could fill

#### Research
I don't like any of the existing solutions, so I'm going to build my own. I HATE ORMs. I don't like abstractions. I really enjoy using raw SQL and I want to be able to use that with Pydantic. Interesting to note that I'm not trying to build a full ORM, just a way to use raw SQL with Pydantic. I really do like the way Psycopg handles SQL in python. I think it might be a good idea to build this on top of Psycopg.

### 1.2 SQL Parsing Libraries
- Investigate SQL parsing libraries (e.g., sqlparse, moz-sql-parser)
- Evaluate their capabilities for query analysis and modification

#### Research
Okay so I'm doing research on sqlparse. So far I like what I see, but it seems incredibly lightweight. You can pass in a raw SQL string, and use ".split()" to get all separate statements. ".format()" will simply pretty print the SQL statement, which is not super useful. SQlParse is non validating. calling ".parse()" will return a tuple of Statement. This seems like it could be useful to break down a query into its components. Each statement has a "tokens" attribute which is a list of tokens. This is interesting, each token represents some part of the SQL statement, and it can have nested children tokens. Very similar to a CST.
Pros:
- Lightweight and easy to integrate
- Useful for basic query analysis and tokenization
- Could help with parameter extraction
Cons:
- Doesn't assist with parameter substitution
- Non-validating, which means we can't rely on it for SQL syntax checking
- May not provide advanced features needed for query optimization
AI opinion:
- Given our focus on PostgreSQL and the desire to work with raw SQL, sqlparse could be a useful tool, but it might not be sufficient on its own. Here's what I think:
1. Parameter handling: We'll need to implement our own parameter substitution mechanism, as sqlparse doesn't handle this. This aligns with your preference for raw SQL control.
2. Query analysis: sqlparse's tokenization could be useful for identifying placeholders ($1, $2, etc.) in PostgreSQL queries. We could use this to match parameters with their positions in the query.
3. Validation: Since sqlparse is non-validating, we might want to consider adding a validation layer, possibly using PostgreSQL's own parser (accessible through psycopg) for more accurate results.
4. Integration with Psycopg: We should investigate how sqlparse can complement Psycopg's features. For instance, we could use sqlparse for initial query analysis and then rely on Psycopg for actual execution and parameter substitution.
5. Performance considerations: We should benchmark sqlparse's performance on large or complex queries to ensure it doesn't become a bottleneck.
6. Custom enhancements: We might need to build additional functionality on top of sqlparse to meet our specific needs, such as PostgreSQL-specific syntax handling or integration with Pydantic models.

### 1.3 Database Drivers
- Research different database drivers (e.g., psycopg2, asyncpg)
- Understand their APIs and how they handle parameter substitution

#### Research
I am leaning towards using psycopg3. I've been using it for a long time. However, I'm open to using something else, if it turns out we need something more advanced and custom. I am learning a lot about SQL databases and how they work, so I'm open to learning something new. That being said, I have done many hours of research into pyscopg2 and 3. Here are my thoughts, in no real order.
- Psycopg is really nice, it allows me to run raw SQL and provides useful tools to do it. I can easily get a connection, run a query, and get the results. The cursor is really useful to get the results back.
- I've experimented deeply with using the cursor. The default return for the cursor was a list of tuples. I did not like this at all, as they were predicated on the order of the columns, and didn't provide any information about the columns. Was annoying when quickly iterating on select statements. I prefer to receive a list of dictionaries, where the keys are the column names. This is now my default.
- Recently I upgraded to pyscopg3. Psycopg3 provides a class row parameter for the cursor. This allows you to provide some class that you want the result rows to be converted into. This was the basis for my old Pydantic specific database functions. I could easily receive a list of Pydantic models, which were already validated! This was inspiration to create this project.
- I don't really know what we want to do for parameter substittution. Psycopg has its own sql.SQL where you can construct/deconstruct an SQL statement. If you provide the individual parameters, and a query with psycopg placeholders, it will automatically handle the substititon. This is nice, but it's sometimes very annoying to have to do.
- I have a couple of ideas. This project could be some kind of adapter between raw SQL and the psycopg.SQL. Then I could pretty much just use all of psycopg's functionality.
- This project could also potentially not use Psycopg and have a more custom implementation. 
- One thing I struggled with in my research was understanding query execution. I'm still not sure how query execution would work with a potential pyscopg adapter.

Pros of using Psycopg:
- Robust and well-maintained PostgreSQL adapter
- Supports both synchronous and asynchronous operations (in Psycopg3)
- Good integration with Python's DB-API
- Handles PostgreSQL-specific data types well
- Allows for raw SQL execution, which aligns with your preferences
Cons of using Psycopg:
- May have performance overhead compared to more lightweight drivers like asyncpg for certain operations
- The transition from Psycopg2 to Psycopg3 might introduce compatibility issues
- Might be overkill if you only need a subset of its features
Could potentially limit the design of your adapter if you conform too closely to its API
AI opinion:
Given your experience with Psycopg and your preference for raw SQL, building on top of Psycopg3 seems like a good starting point. However, I would recommend the following:
- Abstraction layer: Design your adapter with an abstraction layer that doesn't tie you too closely to Psycopg's API. This will allow you to potentially swap out the underlying driver in the future if needed.
- Asynchronous support: Make sure to leverage Psycopg3's async capabilities from the start. This will future-proof your adapter for high-performance scenarios.
- Parameter handling: Implement a flexible parameter substitution system that can work with both Psycopg's native method and your own custom approach if needed.
- Performance testing: Conduct thorough performance tests, comparing Psycopg with other drivers like asyncpg for your specific use cases.
- Advanced features: Explore and potentially incorporate support for advanced PostgreSQL features that Psycopg offers.
Query execution: For query execution, consider implementing a method that takes a raw SQL query and a Pydantic model, handles parameter substitution, executes the query using Psycopg, and returns the results as instances of the Pydantic model.

### 1.4 Pydantic Integration
- Study Pydantic's internals, especially its model parsing and validation mechanisms
- Investigate how Pydantic handles custom types and nested models

#### Research
TODO for now. Leave be.


### 1.5 Python Language Features
- Research Python metaprogramming techniques
- Investigate Python's descriptor protocol and how it could be used for query composition

#### Research
TODO for now. Have done extensive research on Python CST parsing.Leave be.

## 2. Design Decisions

### 2.1 SQL Representation
- Decide how to represent SQL queries internally
  - Options: String-based, AST (Abstract Syntax Tree), or hybrid approach

#### Design
Implementation suggestion:
1. Store the original SQL as a string in the PydanticSQL class.
2. Implement a lazy parsing mechanism that only converts the SQL to an AST when analysis or modification is required.
3. Use sqlparse for initial tokenization and analysis, but consider building a more PostgreSQL-specific parser on top of it for advanced features.
4. Provide methods that work with both the string representation and the AST, allowing users to choose their preferred level of abstraction.
-This approach would allow us to start with a simple, string-based implementation that supports raw SQL, while leaving the door open for more advanced features as the project evolves. It also aligns well with your experience with Psycopg and preference for direct SQL control.

### 2.2 Database Driver Integration
- Decide on the primary database driver to use and how to integrate it
  - Options: Build on top of Psycopg3, create a custom abstraction layer, or support multiple drivers

#### Design
I recommend starting with Psycopg3 as the primary database driver, but with a crucial caveat: implement an abstraction layer.
Here's the proposed approach:
1. Use Psycopg3 as the underlying driver initially.
2. Create an abstraction layer that wraps Psycopg3's functionality. This layer should define a clear interface for database operations that aligns with our project's goals.
3. Implement the core PydanticSQL functionality using this abstraction layer, not directly on Psycopg3.
This approach offers several benefits:
- Leverages Psycopg3's robust features and your familiarity with it
- Allows for rapid initial development
- Provides flexibility to swap out the underlying driver in the future if needed
- Enables custom optimizations or features to be added to the abstraction layer without changing the core PydanticSQL implementation
By using this abstraction layer, we can start with a solid foundation while keeping our options open for future optimizations or even switching to a custom implementation if it proves necessary.

### 2.3 Parameter Handling and Substitution
- Choose a method for parameter handling and substitution that works well with raw SQL and Pydantic models
  - Consider: Psycopg's native method, custom implementation, or a hybrid approach

#### Design
1. Flexible Parameter Input
We should aim for a flexible system that can handle multiple types of parameter inputs:
- Raw Python types (strings, integers, etc.)
- Pydantic models
- Dictionaries
This flexibility will allow users to choose the most convenient method for their use case, whether it's a simple query with a few parameters or a complex operation involving entire Pydantic models.
2. Named Parameters
Adopting a named parameter approach (e.g., :param_name in SQL) could offer several benefits:
- Improved readability of SQL queries
- Easier mapping between input parameters and their use in queries
Reduced risk of errors from mismatched parameter ordering
3. Type Safety and Inference
Balancing automatic type inference with manual type specification is crucial:
- Implement automatic type inference from database schema where possible
- Allow overriding of inferred types when needed
- Use Pydantic models for complex type definitions and validations


### 2.5 Query Execution and Connection Management
- Decide on the approach for query execution and database connection management
  - Consider: Connection pooling, context managers for transactions, and integration with async operations
#### Design
1. Direct Use of Psycopg:
- Utilize psycopg's native query execution methods.
- This approach takes advantage of psycopg's optimized and well-tested execution pipeline.
- It allows us to benefit from future improvements in psycopg without needing to update our execution logic.
2. Connection Management:
- Rely on psycopg's connection pooling capabilities.
- This offloads the complexity of managing database connections to a battle-tested system.
- It can help in optimizing resource usage, especially in high-concurrency scenarios.
3. Transaction Handling:
Use psycopg's transaction management features.
- This ensures ACID compliance and allows for easy implementation of complex transaction patterns.
Decoupling from Parameter Logic
1. Clear Separation:
- Keep parameter handling and query execution as separate concerns.
- This separation allows for easier maintenance and potential future changes to either component.
2. Interface Design:
- Design a clean interface between our parameter handling logic and the query execution.
- This interface should be flexible enough to accommodate different types of queries and parameter styles.
3. Async Support
- Dual Support:
Implement both synchronous and asynchronous query execution methods.
This can be achieved by leveraging psycopg's support for both paradigms.
- Consistent API:
- Design the API so that switching between sync and async is as seamless as possible for the user.
4. Error Handling
- Psycopg Error Translation:
Translate psycopg-specific errors into our own error types where appropriate.
- This provides a consistent error handling experience across our entire adapter.
- Contextual Information:
- Enrich error messages with relevant context from our parameter handling and query preparation steps.
5. Performance Considerations
1. Minimal Overhead:
Ensure that our adapter adds minimal overhead to psycopg's execution process.
- Focus on efficient handoff between our parameter handling and psycopg's execution.
2. Execution Plans:
- Consider exposing psycopg's ability to return execution plans for queries.
- This can be valuable for users looking to optimize their database interactions.
6. Extensibility
1. Driver Abstraction:
- While initially using psycopg, design the execution interface in a way that could potentially support other drivers in the future.
- This doesn't mean building a full abstraction layer now, but rather keeping the possibility in mind during design.

## 3. Core Feature Implementation

### 3.1 Adapter Class Design
- Design the main `PydanticSQL` class structure
- Implement basic query representation and execution

### 3.2 Query Parsing
- Develop or integrate a SQL parsing mechanism
- Implement placeholder extraction and validation

### 3.3 Parameter Handling
- Implement parameter substitution mechanism
- Develop type-safe parameter passing from Pydantic models

### 3.4 Result Mapping
- Create a system to map query results to Pydantic models
- Handle nested data structures and relationships

### 3.5 Transaction Management
- Implement a context manager for handling database transactions
- Ensure proper connection and cursor management

### 3.6 Database Integration
- Develop a database connection management system
- Implement query execution using the chosen database driver

## 4. Testing and Documentation

### 4.1 Unit Testing
- Develop a comprehensive unit test suite for each component

### 4.2 Integration Testing
- Create integration tests with actual database interactions

### 4.3 Documentation
- Write detailed API documentation
- Create usage examples and tutorials

## 5. Performance Optimization

### 5.1 Profiling
- Profile the adapter's performance in various scenarios

### 5.2 Optimization
- Optimize critical paths based on profiling results
- Implement caching mechanisms where appropriate

## 6. Advanced Features

### 6.1 Bulk Operations
- Implement efficient bulk insert and update operations

### 6.2 Async Support
- Add asynchronous query execution capabilities

### 6.3 Schema Validation
- Create utilities for validating Pydantic models against database schema

### 6.4 Model Generation
- Implement automatic Pydantic model generation from database schema
