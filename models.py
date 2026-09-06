from pydantic import BaseModel
from datetime import datetime
from calculator import expand_percent


class Expression(BaseModel):
    expr: str

    def expand_percent(self) -> str:
        return expand_percent(self.expr)

class CalculatorLog(BaseModel):
    timestamp: datetime
    expr: str
    result: float
