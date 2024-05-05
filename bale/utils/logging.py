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
import logging

def setup_logging(level: int = logging.INFO, handler: logging.Handler = None, formatter: str = None):
    if handler is None:
        handler = logging.StreamHandler()

    if formatter is None:
        formatter = '[{asctime}] [{levelname:<8}] {name}: {message}'
    formatter = logging.Formatter(formatter, '%Y-%m-%d %H:%M:%S', style='{')
    handler.setFormatter(formatter)

    library = __name__.partition('.')[0]
    logger = logging.getLogger(library)
    logger.addHandler(handler)
    logger.setLevel(level)