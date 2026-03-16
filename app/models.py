from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict

class Event(BaseModel):

    user_id: str
    event_type: str
    timestamp: datetime
    properties: Optional[Dict] = {}