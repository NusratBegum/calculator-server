import math
from collections import deque
from datetime import datetime

from asteval import Interpreter
from fastapi import APIRouter, Depends

from app.dependencies import expand_percent, get_history
from app.schemas import ExpressionIn, ExpressionOut

router = APIRouter(tags=["calculator"])

# ---------- Safe evaluator ----------
aeval = Interpreter(minimal=True, usersyms={"pi": math.pi, "e": math.e})


@router.post("/calculate")
def calculate(
    expression: ExpressionIn,
    code: str = Depends(expand_percent),
    history: deque[ExpressionOut] = Depends(get_history),
):
    try:
        result = aeval(code)
        # error handle
        if aeval.error:
            msg = "; ".join(str(e.get_error()) for e in aeval.error)
            aeval.error.clear()
            return {"ok": False, "expr": expression.expr, "result": "", "error": msg}
        # not error
        history.append(ExpressionOut(timestamp=datetime.now(), expr=expression.expr, result=result))
        return {"ok": True, "expr": expression.expr, "result": result, "error": ""}

    except Exception as e:
        return {"ok": False, "expr": expression.expr, "error": str(e)}
