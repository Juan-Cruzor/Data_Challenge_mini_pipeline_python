from datetime import datetime
from app.logger import logger

def validate_event(event):
    """The function checks for valid user_id and timestamp in the event
            Args:
                event[dict]:Dictionary conyaining the following structure
                {
                    "event": "purchase_complete",
                    "user_id": "12345",
                    "timestamp": "2023-01-01T12:00:00Z",
                    "properties": {
                        "amount": 100
                    }
                }
    """

    user_id = event.get("user_id")
    timestamp = event.get("timestamp")

    if not user_id:
        logger.warning(f"Event {event} not valid - user_id is missing")
        return False

    try:
        datetime.fromisoformat(timestamp.replace("Z",""))
    except Exception:
        logger.warning(f"Event {event} not valid - wrong timestampformat")
        return False

    return True


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

    properties = event.get("properties",{})

    if event["event"] == "purchase_complete":
        properties.setdefault("amount",0)

    event["properties"] = properties

    return event