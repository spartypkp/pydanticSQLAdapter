# tests/test_query.py

import pytest
from pydantic import BaseModel
from pydantic_sql.query import Query

class User(BaseModel):
    id: int
    name: str

def test_query_initialization():
    sql = "SELECT * FROM users WHERE id = :id"
    params = {"id": 1}
    query = Query(sql, params, User)

    assert query.sql == sql
    assert query.params == params
    assert query.model == User

def test_query_without_params_and_model():
    sql = "SELECT * FROM users"
    query = Query(sql)

    assert query.sql == sql
    assert query.params == {}
    assert query.model is None

def test_query_repr():
    sql = "SELECT * FROM users WHERE id = :id"
    params = {"id": 1}
    query = Query(sql, params, User)

    expected_repr = "Query(sql='SELECT * FROM users WHERE id = :id', params={'id': 1}, model=User)"
    assert repr(query) == expected_repr