#  An API wrapper for Bale written in Python
#  Copyright (c) 2022-2026
#  Kian Ahmadian <devs@python-bale-bot.ir>
#  All rights reserved.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.#  This software is licensed under the GNU General Public License v2.0.
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

from pathlib import Path
from typing import TYPE_CHECKING, Any, Type

if TYPE_CHECKING:
    from bale.attachments import AttachmentType, InputFile


def is_file_valid(obj: Path | str | None) -> Path | None:
    if obj is None:
        return None

    path = Path(obj)
    return path if path.is_file() else None


def parse_file_input(
    file_input: Any,
    attachment_types: (
        Type["AttachmentType"] | tuple[Type["AttachmentType"]] | None
    ) = None,
    filename: str | None = None,
) -> "str | InputFile":
    from bale import InputFile

    if isinstance(file_input, InputFile):
        return file_input

    if isinstance(file_input, bytes):
        return InputFile.from_bytes(file_input, filename)

    if isinstance(file_input, Path) or (
        isinstance(file_input, str) and Path(file_input).exists()
    ):
        return InputFile.from_path(file_input, filename=filename)

    if isinstance(file_input, str):
        return file_input

    if attachment_types and isinstance(file_input, attachment_types):
        return file_input.file_id

    if not isinstance(attachment_types, tuple) and attachment_types is not None:
        attachment_types = (attachment_types,)

    att_names = (
        ", ".join(a.__class__.__name__ for a in attachment_types) + ", "
        if attachment_types
        else ""
    )
    raise TypeError(
        f"You cannot give the file like this. Your file must be one of {att_names}bytes, str and InputFile types."
    )
