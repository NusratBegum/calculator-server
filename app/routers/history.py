from collections import deque
from itertools import islice

from fastapi import APIRouter, Depends

from app.dependencies import get_history
from app.schemas import ExpressionOut

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=list[ExpressionOut])
def read_history(limit: int, history: deque[ExpressionOut] = Depends(get_history)):
    if limit < 0:
        return []
    return list(islice(history, limit))


@router.delete("")
def clear_history(history: deque[ExpressionOut] = Depends(get_history)):
    if not history:
        return {"ok": True, "cleared": False}
    history.clear()
    return {"ok": True, "cleared": True}
