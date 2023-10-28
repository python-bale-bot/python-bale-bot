from typing import Any
import json

__all__ = (
	"ResponseStatusCode",
	"to_json"
)

class ResponseStatusCode:
	OK = 200
	NOT_INCORRECT = 400
	NOT_FOUND = 440
	PERMISSION_DENIED = 403
	RATE_LIMIT = 429

def to_json(obj: Any) -> str:
	return json.dumps(obj)