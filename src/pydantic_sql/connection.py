# src/pydantic_sql/connection.py

from typing import Dict, Any, Optional
import psycopg
from psycopg_pool import ConnectionPool

class ConnectionManager:
    def __init__(self, connection_params: Dict[str, Any], pool_size: int = 10):
        """
        Initialize the ConnectionManager.
        
        :param connection_params: Dictionary containing database connection parameters.
        :param pool_size: The maximum number of connections to keep in the pool.
        """
        self.connection_params = connection_params
        self.pool: Optional[ConnectionPool] = None
        self.pool_size = pool_size

    def initialize_pool(self):
        """
        Initialize the connection pool.
        This should be called before any database operations are performed.
        """
        if self.pool is None:
            self.pool = ConnectionPool(
                conninfo=self.connection_params,
                min_size=1,
                max_size=self.pool_size
            )

    def get_connection(self) -> psycopg.Connection:
        """
        Get a connection from the pool.
        
        :return: A database connection.
        """
        if self.pool is None:
            raise Exception("Connection pool not initialized. Call initialize_pool() first.")
        return self.pool.getconn()

    def release_connection(self, conn: psycopg.Connection):
        """
        Release a connection back to the pool.
        
        :param conn: The connection to release.
        """
        if self.pool is not None:
            self.pool.putconn(conn)

    def close_pool(self):
        """
        Close the connection pool.
        This should be called when the application is shutting down.
        """
        if self.pool is not None:
            self.pool.close()
            self.pool = None

    def __enter__(self):
        """
        Context manager entry point.
        Initializes the pool if it hasn't been initialized.
        """
        self.initialize_pool()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point.
        Closes the pool when exiting the context.
        """
        self.close_pool()