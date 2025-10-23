from fastapi import APIRouter
from ml.eval_metrics import latest_metrics

router = APIRouter()

@router.get("/metrics")
def metrics():
    return latest_metrics()
