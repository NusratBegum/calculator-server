import math
from collections import deque
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from asteval import Interpreter

from calculator import expand_percent

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
def calculate(expr: str):
    try:
        code = expand_percent(expr)
        result = aeval(code)
        # error handle 
        if aeval.error:
            msg = "; ".join(str(e.get_error()) for e in aeval.error)
            aeval.error.clear()
            return {"ok": False, "expr": expr, "result": "", "error": msg}
        # not error
        # TODO: Add history
        time = datetime.now()
        cal_history = {
          "timestamp": time,
           "expr": expr, 
           "result": result
        }
        db.append(cal_history)
        return {"ok": True, "expr": expr, "result": result, "error": ""}

    
    except Exception as e:
        return {"ok": False, "expr": expr, "error": str(e)}

# TODO GET /hisory
@app.get("/history")
def history(limit:int):
    if limit < 0:
        return {"ok": False, "error": "Limit can not be negative"}
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





