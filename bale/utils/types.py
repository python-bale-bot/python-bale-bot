from typing import Union, Dict, Any, TypeVar, Callable, Coroutine, TYPE_CHECKING
from pathlib import Path
if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from bale import Audio, Document, Location, PhotoSize, Video, Animation, Voice

JSONDICT = Dict[str, Any]
T = TypeVar('T')
UT = TypeVar('UT')
Coro = Coroutine[Any, Any, T]
CoroT = TypeVar('CoroT', bound=Callable[..., Coro[Any]])

FileInput = Union[str, bytes, Path]

AttachmentType = Union[
    "Audio",
    "Document",
    "Location",
    "PhotoSize",
    "Video",
    "Animation",
    "Voice"
]