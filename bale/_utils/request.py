#  An API wrapper for Bale written in Python
#  Copyright (c) 2022-2026
#  Kian Ahmadian <devs@python-bale-bot.ir>
#  All rights reserved.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeAlias

from aiohttp import FormData

from .._baleobject import BaleObject
from .._utils.object import json
from .._utils.typehint import MISSING
from ..attachments import InputFile
from ..constants import StringEnum

if TYPE_CHECKING:
    from bale import (InputMediaAnimation, InputMediaAudio, InputMediaDocument,
                      InputMediaPhoto, InputMediaVideo)

    MediaInput: TypeAlias = (
        InputMediaPhoto
        | InputMediaVideo
        | InputMediaAnimation
        | InputMediaAudio
        | InputMediaDocument
    )

__all__ = (
    "ResponseStatusCode",
    "to_json",
    "build_form_data",
    "build_payload",
)


class ResponseStatusCode:
    OK = 200
    BAD_REQUEST = 400
    INCORRECT = BAD_REQUEST
    NOT_FOUND = 404
    PERMISSION_DENIED = 403
    UNAUTHORIZED = 401
    FORBIDDEN = PERMISSION_DENIED
    RATE_LIMIT = 429
    BAD_GATEWAY = 502


def to_json(obj: Any) -> str:
    return json.dumps(obj)


def _get_parameter_value(value: Any):
    if isinstance(value, StringEnum):
        return value.value
    if isinstance(value, BaleObject):
        return value.to_json()

    return value


def _parse_form_data_field_value(value: Any):
    if isinstance(value, int):
        value = str(value)

    return value


def build_media_group(
    payload: dict[str, Any],
) -> tuple[dict[str, Any] | None, FormData | None]:
    media: list[MediaInput] = payload["media"]
    use_form_data = any(isinstance(i.media, InputFile) for i in media)

    if use_form_data:
        form = FormData()

        media_array = []

        for idx, m in enumerate(media, start=1):
            media_type = m.type
            media_value = m.media
            media_caption = m.caption

            media_item = {"type": media_type}
            if media_caption:
                media_item["caption"] = media_caption

            if isinstance(media_value, InputFile):
                field_name = f"{media_type}_{idx}"
                media_item["media"] = f"attach://{field_name}"
                field_kwargs = media_value.to_multipart_payload()
                form.add_field(name=field_name, **field_kwargs)
            else:
                media_item["media"] = _parse_form_data_field_value(media_value)

            media_array.append(media_item)

        for key, value in build_payload(payload).items():
            if key != "media":
                form.add_field(key, _parse_form_data_field_value(value))
        form.add_field("media", json.dumps(media_array))

        return None, form

    payload["media"] = [i.to_dict() for i in media]

    return payload, None


def maybe_form_data(
    data: dict, form_data: FormData | None = None
) -> tuple[dict[str, Any] | None, FormData | None]:
    use_form_data = any(isinstance(value, InputFile) for key, value in data.items())
    if use_form_data:
        return None, build_form_data(data)

    return build_payload(data), None


def build_form_data(data: Any) -> FormData:
    if isinstance(data, FormData):
        return data

    form_data = FormData(quote_fields=False)
    if isinstance(data, dict):
        for key, value in data.items():
            if value is MISSING:
                continue

            if isinstance(value, InputFile):
                field_kwargs = value.to_multipart_payload()
                form_data.add_field(name=key, **field_kwargs)
            else:
                form_data.add_field(name=key, value=_parse_form_data_field_value(value))

    return form_data


def build_payload(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if not payload:
        payload = {}

    payload = {
        key: _get_parameter_value(value)
        for key, value in payload.items()
        if value is not MISSING
    }

    return payload
