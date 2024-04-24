from typing import Any, Type, TYPE_CHECKING, Optional
import json
if TYPE_CHECKING:
	from bale.request.parser import ResponseParser
	from bale.error import BaleError

__all__ = (
	"ResponseStatusCode",
	"to_json",
	"find_error_class"
)

class ResponseStatusCode:
	OK = 200
	NOT_INCORRECT = 400
	NOT_FOUND = 440
	PERMISSION_DENIED = 403
	RATE_LIMIT = 429

def to_json(obj: Any) -> str:
	return json.dumps(obj)

def find_error_class(response: "ResponseParser") -> Optional[Type["BaleError"]]:
	from bale.error import __ERROR_CLASSES__

	for err_obj in __ERROR_CLASSES__:
		if err_obj.STATUS_CODE == response.original_response.status or err_obj.check_response(response):
			return err_obj

	return None