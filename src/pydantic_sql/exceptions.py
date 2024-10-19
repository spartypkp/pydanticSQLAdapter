# src/pydantic_sql/exceptions.py

class PydanticSQLException(Exception):
    """Base exception class for PydanticSQL."""
    pass

class ConnectionError(PydanticSQLException):
    """Raised when there's an issue with database connection."""
    pass

class QueryError(PydanticSQLException):
    """Raised when there's an error in query execution."""
    pass

class ParameterError(PydanticSQLException):
    """Raised when there's an issue with query parameters."""
    pass

class ResultMappingError(PydanticSQLException):
    """Raised when there's an error mapping query results to Pydantic models."""
    pass

class ConfigurationError(PydanticSQLException):
    """Raised when there's a configuration issue."""
    pass

class TransactionError(PydanticSQLException):
    """Raised when there's an error during transaction management."""
    pass

class ValidationError(PydanticSQLException):
    """Raised when there's a validation error with Pydantic models."""
    pass

# You can add more specific exceptions as needed

def handle_db_error(error: Exception) -> PydanticSQLException:
    """
    Convert database-specific errors to PydanticSQL exceptions.
    
    :param error: The original database error.
    :return: A PydanticSQLException.
    """
    # This is a placeholder implementation. You'll need to expand this
    # to handle specific database errors and convert them to appropriate
    # PydanticSQL exceptions.
    return QueryError(str(error))

