from typing import Union, Dict, Any, TypeVar, Callable, Coroutine, TYPE_CHECKING
from pathlib import Path
if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from bale import (
        Audio,
        Document,
        Location,
        PhotoSize,
        Video,
        Animation,
        Voice,
        InputMedia,
        InputMediaPhoto,
        InputMediaVideo,
        InputMediaAnimation,
        InputMediaAudio,
        InputMediaDocument
    )

JSONDICT = Dict[str, Any]
T = TypeVar('T')
UT = TypeVar('UT')
Coro = Coroutine[Any, Any, T]
CoroT = TypeVar('CoroT', bound=Callable[..., Coro[Any]])

FileInput = Union[str, bytes, Path]

AttachmentType = Union[
    "Audio",
    "Document",
    "PhotoSize",
    "Video",
    "Animation",
    "Voice"
]

MediaInput = Union[
    "InputMedia",
    "InputMediaPhoto",
    "InputMediaVideo",
    "InputMediaAnimation",
    "InputMediaAudio",
    "InputMediaDocument"
]