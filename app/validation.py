from app.models import Event
from pydantic import ValidationError


def validate_event(raw_event):

    try:
        event = Event(**raw_event)
        return event.dict()

    except ValidationError:
        return None


def normalize_event(event):
    """Function that normalizes events by setting a default amount
        Args:
            event[dict]:Dictionary conyaining the following structure
            {
                "event": "string",
                "user_id": "string",
                "timestamp": "date format",
                "properties": dictionary {
                    "amount": 100
                }
            }
    """

    properties = event.get("properties", {})

    if event["event"] == "purchase_complete":
        properties.setdefault("amount", 0)

    event["properties"] = properties

    return event