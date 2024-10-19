# src/pydantic_sql/adapter.py

from typing import Any, Dict, List, Optional, Union, Type
from pydantic import BaseModel
from .query import Query
from .connection import ConnectionManager
from .exceptions import PydanticSQLException, handle_db_error
from .parameter_handler import ParameterHandler
from .result_mapper import ResultMapper

class PydanticSQL:
    def __init__(self, connection_params: Dict[str, Any], pool_size: int = 10):
        """
        Initialize the PydanticSQL adapter.

        :param connection_params: Database connection parameters.
        :param pool_size: Size of the connection pool.
        """
        self.connection_manager = ConnectionManager(connection_params, pool_size)
        self.parameter_handler = ParameterHandler()
        self.result_mapper = ResultMapper()

    def connect(self) -> None:
        """Establish a connection to the database."""
        self.connection_manager.initialize_pool()

    def close(self) -> None:
        """Close all database connections."""
        self.connection_manager.close_pool()

    def execute(self, query: Query) -> List[Union[Dict[str, Any], BaseModel]]:
        """
        Execute a query and return the results.

        :param query: The Query object to execute.
        :return: List of results as dictionaries or Pydantic models.
        """
        try:
            prepared_query = query.prepare()
            executable_sql, params = prepared_query.get_executable()

            with self.connection_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(executable_sql, params)
                    raw_results = cur.fetchall()
                    column_names = [desc[0] for desc in cur.description]
                    results = [dict(zip(column_names, row)) for row in raw_results]

            return query.map_results(results)
        except Exception as e:
            raise handle_db_error(e)

    def execute_many(self, query: Query, params_list: List[Union[Dict[str, Any], BaseModel]]) -> None:
        """
        Execute a query multiple times with different parameters.

        :param query: The Query object to execute.
        :param params_list: List of parameter sets to use for multiple executions.
        """
        try:
            prepared_query = query.prepare()
            executable_sql, _ = prepared_query.get_executable()

            processed_params_list = [
                self.parameter_handler.process_parameters(params)
                for params in params_list
            ]

            with self.connection_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.executemany(executable_sql, processed_params_list)
                conn.commit()
        except Exception as e:
            raise handle_db_error(e)

    def transaction(self):
        """
        Start a new transaction.

        :return: A context manager for the transaction.
        """
        return self.connection_manager.transaction()

    def create_query(
        self,
        sql: str,
        params: Optional[Union[Dict[str, Any], BaseModel, List[Union[Dict[str, Any], BaseModel]]]] = None,
        model: Optional[Type[BaseModel]] = None,
        name: Optional[str] = None
    ) -> Query:
        """
        Create a new Query object.

        :param sql: The SQL query string.
        :param params: Query parameters.
        :param model: Pydantic model for result mapping.
        :param name: Optional name for the query.
        :return: A new Query object.
        """
        return Query(sql, params, model, name)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()