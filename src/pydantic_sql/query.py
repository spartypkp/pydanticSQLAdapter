# src/pydantic_sql/query.py

from typing import Any, Dict, List, Optional, Type, Union
from pydantic import BaseModel
from .connection import PostgreSQLConnection
from .exceptions import DynamicParameterError
import re

class Query:
    """
    Represents an SQL query with support for value parameters and dynamic parameters.

    Value parameters ($$) can be inferred from the DB schema and are represented by a placeholder.
    Dynamic parameters ({}) are provided within the SQL string through f-string formatting.

    The query needs to be prepared before execution, which involves:
    1. Inferring types for value parameters (requires DB connection).
    2. Sanitizing and inferring types for dynamic parameters.

    Preparation can be done at runtime or ahead of time in watch mode.
    """
    def __init__(
        self,
        sql: str,
        param_model: Optional[Type[BaseModel]] = None,
        result_model: Optional[Type[BaseModel]] = None
    ):
        """
        Initialize a Query object.

        :param sql: The SQL query string with placeholders for value params ($$) and dynamic params ({}).
        :param param_model: Optional Pydantic model to override inferred parameter types.
        :param result_model: Optional Pydantic model to override inferred result types.
        """
        self.original_sql = sql
        self.sql = sql
        self.param_model = param_model
        self.result_model = result_model
        self.inferred_param_model: Optional[Type[BaseModel]] = None
        self.inferred_result_model: Optional[Type[BaseModel]] = None
        self.dynamic_params: Dict[str, Any] = {}
        self.is_prepared = False

    def _validate_dynamic_params(self) -> None:
        """
        Validate dynamic parameters in the SQL query.
        Replace f-string formatting with PostgreSQL-style numbered placeholders.
        Add dynamic parameter information to the param_model.
        """
        pattern = r'\{([^}]+)\}'
        placeholder_counter = 0
        param_mapping: Dict[str, int] = {}
        
        def replace_with_placeholder(match):
            nonlocal placeholder_counter
            param_name = match.group(1)
            if param_name not in self.dynamic_params:
                raise DynamicParameterError(f"Dynamic parameter '{param_name}' not provided")
            
            if param_name not in param_mapping:
                placeholder_counter += 1
                param_mapping[param_name] = placeholder_counter
            
            placeholder = f"${param_mapping[param_name]}"
            
            # Add to param_model
            self._add_to_param_model(param_name, type(self.dynamic_params[param_name]))
            
            return placeholder

        # Update SQL with placeholders
        self.sql = re.sub(pattern, replace_with_placeholder, self.original_sql)
        
        # Update dynamic_params to be in the correct order for execution
        self.ordered_params = [self.dynamic_params[param] for param in sorted(param_mapping, key=param_mapping.get)]
       


    def _add_to_param_model(self, param_name: str, param_type: Type) -> None:
        """
        Add a dynamic parameter to the param_model.
        This is a placeholder method and should be implemented based on how you want to handle
        dynamic parameters in your param_model.
        """
        # Implementation depends on how you want to handle dynamic params in your model
        # For example, you might want to create a new Pydantic model or update an existing one
        pass

    def _prepare(self, db_connection: PostgreSQLConnection) -> None:
        """
        Internal method to prepare the query. This is called automatically and not exposed to the user.

        Watch mode: Calls early, before execution.
        Runtime mode: Calls at runtime, default.
        """
        if self.is_prepared:
            return
        
        # Validate the dynamic parameters to construct the updated query.
        self._validate_dynamic_params()
        # Allow param or result model overrides, otherwise infer from db schema.
        if self.param_model is None:
            self.inferred_param_model = self._infer_param_model(db_connection)
        else:
            self.inferred_param_model = self.param_model

        if self.result_model is None:
            self.inferred_result_model = self._infer_result_model(db_connection)
        else:
            self.inferred_result_model = self.result_model

        

        self.is_prepared = True
        # Future Feature: Automatically edit source code to directly type the inferred models.

    def _infer_param_model(self, db_connection) -> Type[BaseModel]:
        """
        Infer the parameter model from the SQL query and database schema.
        
        :param db_connection: Database connection for inferring types.
        :return: Inferred Pydantic model for parameters.
        """
        # Implementation for inferring parameter types
        ...

    def _infer_result_model(self, db_connection) -> Type[BaseModel]:
        """
        Infer the result model from the SQL query and database schema.
        
        :param db_connection: Database connection for inferring types.
        :return: Inferred Pydantic model for results.
        """
        # Implementation for inferring result types
        ...

    def run(self, value_params: Dict[str, Any], db_connection: Optional[PostgreSQLConnection] = None) -> List[Union[Dict[str, Any], BaseModel]]:
        """
        Execute the query with the provided value parameters.
        
        :param value_params: Dictionary of value parameters.
        :param db_connection: Optional database connection. If not provided, uses the config file.
        :return: Query results as either dictionaries or model instances.
        """
        all_params = {**value_params, **self.dynamic_params}
        self._prepare(db_connection)
        
        
        results = self._execute_query(value_params, db_connection)
        return self._map_results(results)


    def _execute_query(self, params: Dict[str, Any], db_connection: PostgreSQLConnection) -> List[Dict[str, Any]]:
        """
        Execute the SQL query using the provided parameters.
        
        :param params: Combined dictionary of value and dynamic parameters.
        :param db_connection: Database connection for executing the query.
        :return: Raw query results.
        """
        # This is where you'd use your database connection to execute the query
        # The actual implementation will depend on your database driver
        # For example, with psycopg2:
        # with db_connection.cursor() as cursor:
        #     cursor.execute(self.sql, params)
        #     return cursor.fetchall()
        pass

    def _map_results(self, results: List[Dict[str, Any]]) -> List[Union[Dict[str, Any], BaseModel]]:
        """
        Map the query results to the appropriate model.
        
        :param results: Raw query results.
        :return: Mapped results as either dictionaries or model instances.
        """
        model = self.result_model or self.inferred_result_model
        if model:
            return [model(**row) for row in results]
        return results

    def __repr__(self) -> str:
        return (f"Query(sql={self.sql!r}, "
                f"param_model={self.param_model.__name__ if self.param_model else None}, "
                f"result_model={self.result_model.__name__ if self.result_model else None})")