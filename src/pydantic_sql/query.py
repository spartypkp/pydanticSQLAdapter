# src/pydantic_sql/query.py

from typing import Any, Dict, List, Optional, Type, Union
from pydantic import BaseModel
from .parameter_handler import ParameterHandler
from .result_mapper import ResultMapper

class Query:
    def __init__(
        self,
        sql: str,
        params: Optional[Union[Dict[str, Any], BaseModel, List[Union[Dict[str, Any], BaseModel]]]] = None,
        model: Optional[Type[BaseModel]] = None,
        name: Optional[str] = None
    ):
        """
        Initialize a Query object.

        :param sql: The SQL query string.
        :param params: Query parameters (dict, Pydantic model, or list of either).
        :param model: Optional Pydantic model to map results to.
        :param name: Optional name for the query (useful for logging or caching).
        """
        self.sql = sql
        self.raw_params = params
        self.model = model
        self.name = name
        self.processed_params: Dict[str, Any] = {}
        self.parameter_handler = ParameterHandler()
        self.result_mapper = ResultMapper()

    def prepare(self) -> 'Query':
        """
        Prepare the query by processing parameters and validating the SQL.
        
        :return: Self, for method chaining.
        """
        if self.raw_params:
            self.processed_params = self.parameter_handler.process_parameters(self.raw_params)
        self.validate()
        return self

    def validate(self) -> None:
        """
        Validate the SQL query and parameters.
        
        :raises ValueError: If validation fails.
        """
        # TODO: Implement query validation logic
        self.parameter_handler.validate_parameters(self.sql, self.processed_params)

    def get_executable(self) -> tuple[str, Dict[str, Any]]:
        """
        Get the executable query and processed parameters.
        
        :return: A tuple of (executable_sql, processed_parameters).
        """
        executable_sql = self.parameter_handler.substitute_parameters(self.sql, self.processed_params)
        return executable_sql, self.processed_params

    def map_results(self, results: List[Dict[str, Any]]) -> List[Union[Dict[str, Any], BaseModel]]:
        """
        Map the query results to the specified model or return as dictionaries.
        
        :param results: The raw query results.
        :return: Mapped results as either dictionaries or model instances.
        """
        return self.result_mapper.map_results(results, self.model)

    def __repr__(self) -> str:
        return f"Query(sql={self.sql!r}, params={self.raw_params!r}, model={self.model.__name__ if self.model else None}, name={self.name!r})"