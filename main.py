import math
from collections import deque
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from asteval import Interpreter
from models import Expression, CalculatorLog

HISTORY_MAX = 1000
# HISTORY (in-memory for now)
history = deque(maxlen=HISTORY_MAX)

app = FastAPI(title="Mini Calculator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Safe evaluator ----------
aeval = Interpreter(minimal=True, usersyms={"pi": math.pi, "e": math.e})

db = []

@app.post("/calculate")
def calculate(use_expr: Expression):
    try:
        code = use_expr.expand_percent()
        result = aeval(code)
        # error handle 
        if aeval.error:
            msg = "; ".join(str(e.get_error()) for e in aeval.error)
            aeval.error.clear()
            return {"ok": False, "expr": use_expr.expr, "result": "", "error": msg}
        # not error
        # TODO: Add history
        time = datetime.now()
        cal_history = {
          "timestamp": time,
           "expr": use_expr.expr, 
           "result": result
        }
        db.append(cal_history)
        return {"ok": True, "expr": use_expr.expr, "result": result, "error": ""}

    
    except Exception as e:
        return {"ok": False, "expr": use_expr.expr, "error": str(e)}

# TODO GET /hisory
@app.get("/history", response_model=list[CalculatorLog])
def history(limit:int):
    if limit < 0:
        return[]
    else:
        return db[:limit]


# TODO DELETE /history
@app.delete("/history")
def history_clear():
    if db == []:
        return {"ok": True, "cleared": False}
    else:
        db.clear()
        return {"ok": True, "cleared": True}





