from app.dependencies import expand_percent
from app.schemas import ExpressionIn


def expand(expr: str) -> str:
    """Call the expand_percent dependency directly with an ExpressionIn."""
    return expand_percent(ExpressionIn(expr=expr))


def test_add_percent():
    """Test addition where B% means 'B percent of A'."""
    assert expand("5 + 10%") == "5 + ((10/100)*5)"

def test_subtract_percent():
    """Test subtraction where B% means 'B percent of A'."""
    assert expand("20 - 30%") == "20 - ((30/100)*20)"

def test_multiply_percent():
    """Test multiplication where B% means 'B divided by 100'."""
    assert expand("15 * 25%") == "15 * (25/100)"

def test_divide_percent():
    """Test division where B% means 'B divided by 100'."""
    assert expand("40 / 50%") == "40 / (50/100)"

def test_multiple_operations():
    """Test expressions with multiple A op B% operations."""
    assert expand("3 * 4% + 2 / 1%") == "3 * (4/100) + 2 / (1/100)"

def test_standalone_100_percent():
    """Test standalone percentage (100%)."""
    assert expand("100%") == "(100/100)"

def test_two_standalone_percents():
    """Test expression with two standalone percentages."""
    assert expand("10% + 20%") == "(10/100) + (20/100)"
