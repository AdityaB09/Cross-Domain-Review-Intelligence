# backend/services/state_store.py

from typing import List, Dict, Any
from threading import Lock

# Pretend "database" of raw reviews we've seen (strings)
GLOBAL_REVIEWS: List[Dict[str, Any]] = []
REVIEWS_LOCK = Lock()

# Pretend "aspect analytics table"
# aspect -> { "count": int, "total_sent": float }
GLOBAL_ASPECT_COUNTS: Dict[str, Dict[str, float]] = {}
ASPECT_LOCK = Lock()
