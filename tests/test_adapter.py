# tests/test_adapter.py

import pytest
from pydantic import BaseModel
from pydantic_sql.adapter import PydanticSQL
from pydantic_sql.query import Query
import os
# Mock connection parameters (you'll need to replace these with actual test database credentials)
TEST_CONNECTION_PARAMS = {
    "dbname": os.getenv("TEST_DB_NAME"),
    "user": os.getenv("TEST_DB_USER"),
    "password": os.getenv("TEST_DB_PASSWORD"),
    "host": os.getenv("TEST_DB_HOST"),
}

class User(BaseModel):
    id: int
    name: str
    email: str

def test_pydanticsql_initialization():
    db = PydanticSQL(TEST_CONNECTION_PARAMS)
    assert db.connection_params == TEST_CONNECTION_PARAMS
    assert db.connection is None

@pytest.mark.parametrize("use_model", [True, False])
def test_execute_query(use_model):
    db = PydanticSQL(TEST_CONNECTION_PARAMS)
    
    # You'll need to set up a test database and insert some test data
    sql = "SELECT id, name, email FROM users WHERE id = :id"
    params = {"id": 1}
    model = User if use_model else None
    
    query = Query(sql, params, model)
    result = db.execute(query)
    
    assert len(result) == 1
    if use_model:
        assert isinstance(result[0], User)
    else:
        assert isinstance(result[0], dict)
    
    assert result[0]['id'] == 1
    assert 'name' in result[0]
    assert 'email' in result[0]

def test_context_manager():
    with PydanticSQL(TEST_CONNECTION_PARAMS) as db:
        assert db.connection is not None
        assert not db.connection.closed
    
    assert db.connection.closed