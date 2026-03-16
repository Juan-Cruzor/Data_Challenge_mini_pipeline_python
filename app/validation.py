from pydantic import TypeAdapter,ValidationError
from app.models import Event

# According to the pydantic documentation, creating an adapter is more efficient.
adapter=TypeAdapter(Event)

def validate_event(raw):
    """Function that validates the event using the pydantic models.
        Args:
            raw[dict]: The raw event data.
        Returns:
            model_dump[dict]: The validated and normalized event data, or None if validation fails.
            """
    try:
        return adapter.validate_python(raw).model_dump()
    except ValidationError:
        return None