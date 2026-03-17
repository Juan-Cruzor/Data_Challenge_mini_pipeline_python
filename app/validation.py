from pydantic import TypeAdapter, ValidationError
from app.models import Event

# TypeAdapter is more efficient than wrapping in a model — recommended by Pydantic v2 docs.
adapter = TypeAdapter(Event)


def validate_event(raw):
    """
    Validate and normalize a raw event dict using Pydantic.

    Returns the validated event as a plain dict, or None if validation fails.
    Failures are silently dropped here; the pipeline counts them as skipped.
    """
    try:
        return adapter.validate_python(raw).model_dump()
    except ValidationError:
        return None
