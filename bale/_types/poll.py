# An API wrapper for Bale written in Python
# Copyright (c) 2022-2026
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from typing import Literal, TypedDict

__all__ = ("Poll",)


class PollOption(TypedDict):
    persistent_id: str
    text: str
    voter_count: int


class Poll(TypedDict):
    id: str
    question: str
    options: list["PollOption"]
    total_voter_count: int
    is_closed: bool
    is_anonymous: bool
    type: Literal["REGULAR", "QUIZ"]
    allows_multiple_answers: bool
    allows_revoting: bool
    members_only: bool
