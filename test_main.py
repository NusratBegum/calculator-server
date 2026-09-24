import pytest
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from app.main import app
from app.dependencies import history as db
from app.schemas import ExpressionIn as Expression, ExpressionOut as CalculatorLog

client = TestClient(app)

# Validates a whole JSON array against the CalculatorLog model in one call.
HistoryList = TypeAdapter(list[CalculatorLog])


@pytest.fixture(autouse=True)
def clean_db():
    """Every test starts and ends with an empty history."""
    db.clear()
    yield
    db.clear()


def post_expr(expr: str):
    """Send the expression as query parameters built from the Expression model."""
    return client.post("/calculate", params=Expression(expr=expr).model_dump())


def test_basic_division():
    r = post_expr("30/4")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 7.5) < 1e-9

def test_percent_subtraction():
    r = post_expr("100 - 6%")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 94.0) < 1e-9

def test_standalone_percent():
    r = post_expr("6%")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 0.06) < 1e-9

def test_invalid_expr_returns_ok_false():
    r = post_expr("2**(3")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False
    assert "error" in data and data["error"] != ""


# TODO Add more tests
def test_limit_zero():
    post_expr("1+1")
    r = client.get("/history", params={"limit": 0})
    assert r.status_code == 200
    logs = HistoryList.validate_python(r.json())
    assert logs == []

def test_limit_neg():
    r = client.get("/history", params={"limit": -1})
    assert r.status_code == 200
    # main.py treats a negative limit as "no rows" rather than an error.
    logs = HistoryList.validate_python(r.json())
    assert logs == []

def test_limit_pos():
    post_expr("1+1")
    post_expr("2+2")
    r = client.get("/history", params={"limit": 50})
    assert r.status_code == 200
    logs = HistoryList.validate_python(r.json())
    assert len(logs) <= 50
    assert all(isinstance(log, CalculatorLog) for log in logs)
    assert logs[0].expr == "1+1"
    assert logs[0].result == 2.0

def test_del_empty():
    r = client.delete("/history")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["cleared"] is False

def test_actual_del():
    post_expr("1+1")
    r = client.delete("/history")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["cleared"] is True

def test_del_twice():
    post_expr("1+1")
    r1 = client.delete("/history")
    r2 = client.delete("/history")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["cleared"] is True
    assert r2.json()["cleared"] is False
