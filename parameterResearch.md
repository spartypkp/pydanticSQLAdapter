Inferable Parameters:
These are typically values used in WHERE clauses, INSERT statements, or other parts of the query where they correspond directly to column values. They can be inferred from the database schema because they relate to specific columns with known data types.
Possible names:
Column-bound parameters
Value parameters
Data parameters
Schema-inferable parameters

Non-inferable Parameters:
These are typically used for table names, column names, or other parts of the SQL structure that can't be directly inferred from the schema. They often require special handling to ensure SQL injection prevention.
Possible names:
Structural parameters
Identifier parameters
Schema parameters
Dynamic SQL elements


In the industry, you might encounter related concepts:
1. Prepared Statements: These typically handle the inferable parameters, allowing for efficient query planning and SQL injection prevention.
Dynamic SQL: This often involves the non-inferable parameters, where parts of the SQL structure itself are dynamically generated.
Query Building: ORMs and query builders often distinguish between value bindings (inferable) and identifiers (non-inferable) in their APIs.
While there's no single "correct" terminology, for the purposes of your project, you could consider terms like:
"Value Parameters" vs. "Structural Parameters"
"Column-Bound Parameters" vs. "Identifier Parameters"
"Inferable Parameters" vs. "Dynamic SQL Elements"