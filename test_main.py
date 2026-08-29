from fastapi.testclient import TestClient
from main import app, db  # or whatever your app module is

client = TestClient(app)

def test_basic_division():
    r = client.post("/calculate", params={"expr": "30/4"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 7.5) < 1e-9

def test_percent_subtraction():
    r = client.post("/calculate", params={"expr": "100 - 6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 94.0) < 1e-9

def test_standalone_percent():
    r = client.post("/calculate", params={"expr": "6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 0.06) < 1e-9

def test_invalid_expr_returns_ok_false():
    r = client.post("/calculate", params={"expr": "2**(3"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False
    assert "error" in data and data["error"] != ""


# TODO Add more tests
def test_limit_zero():
    r = client.get("/history", params={"limit":0})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_limit_neg():
    r = client.get("/history", params={"limit":-1})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False
    assert "error" in data and data["error"] == "Limit can not be negative"

def test_limit_pos():
    r = client.get("/history", params={"limit":50})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) <= 50

def test_del_empty():
    db.clear()
    r = client.delete("/history")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["cleared"] is False

def test_actual_del():
    client.post("/calculate", params={"expr": "1+1"})
    r = client.delete("/history")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["cleared"] is True

def test_del_twice():
    client.post("/calculate", params={"expr": "1+1"})
    r1 = client.delete("/history")
    r2 = client.delete("/history")
    assert r1.status_code == 200
    assert r2.status_code == 200
    data1 = r1.json()
    data2 = r2.json()
    assert data1["cleared"] is True
    assert data2["cleared"] is False
