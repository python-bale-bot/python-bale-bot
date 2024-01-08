# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from __future__ import annotations
from typing import Optional
from bale import BaleObject

__all__ = (
    "Location",
)

class Location(BaleObject):
    """This object shows a Location

    Attributes
    ----------
        longitude: :class:`int`
            Location longitude
        latitude: :class:`int`
            Location latitude
        horizontal_accuracy: Optional[:class:`int`]
            The radius of uncertainty for the location, measured in meters; 0-1500.
    """
    __slots__ = (
        "longitude",
        "latitude",
        "horizontal_accuracy"
    )

    def __init__(self, longitude: int, latitude: int, horizontal_accuracy: Optional[int] = None):
        super().__init__()
        self.longitude = longitude
        self.latitude = latitude
        self.horizontal_accuracy = horizontal_accuracy
        self._id = (longitude, latitude, horizontal_accuracy)

        self._lock()

    @property
    def link(self) -> str:
        """:class:`str`: Export location link from Google map"""
        return f"https://maps.google.com/maps?q=loc:{self.longitude},{self.latitude}"

