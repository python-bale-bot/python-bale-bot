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

import re
from typing import Union, List, Optional, Tuple
from inspect import signature, Parameter

from bale import Update, Message
from bale.checks.basecheck import BaseCheck
from .basehandler import BaseHandler


class CommandHandler(BaseHandler):
    """This object shows a Message Handler.
   It's a handler class to handle Messages.

   Parameters
   ----------
       command: Union[str, List[str]]
           The list of commands that the handler is required to cover. It can be a string or a list of strings.
       check: Optional[Callable[["Update"], bool]]
           The check function for this handler.

           .. hint::
               Called in :meth:`check_new_update`, when new update confirm. This checker indicates whether the Update should be covered by the handler or not.
       has_param: :obj:`int` | :obj:`bool`, optional | :obj:`None`
           A :obj:`bool`, optional and :obj:`int` value that specifies how many parameters the entered command should have.

           - If the command should not have a parameter, its value should be ":obj:`False`".
           - If the command can have any parameter and the :attr:`callback` function can handle it, its value should be ":obj:`True`".
           - If the command must have limited parameters, its value must be the number of parameters that can be covered.
   """
    __slots__ = (
        "commands",
        "check",
        "has_param"
    )

    def __init__(self, command: Union[str, List[str]], check: Optional[BaseCheck] = None,
                 has_param: Optional[Union[int, bool]] = None):
        super().__init__()
        command = list(command) if not isinstance(command, list) else command

        for comm in command:
            if not re.match(r"^[\da-z_]{1,32}$", comm):
                raise ValueError(f"command {comm} must be has valid characters")

        if check and not isinstance(check, BaseCheck):
            raise TypeError(
                "check param must be type of BaseCheck"
            )

        self.commands = [comm.lower() for comm in command]
        self.check = check
        self.has_param = has_param

    def _check_params_correct(self, args: List[str]):
        params = []
        remaining_parameters_count = len(args)
        sig = signature(self.callback)
        for name, param_obj in sig.parameters.items():
            if param_obj.kind in [Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD]:
                return params + (args[len(params):])

            params[len(params)] = (name, args[len(args) - remaining_parameters_count])
            remaining_parameters_count -= 1

        if remaining_parameters_count != 0:
            return False

        return params

    def check_new_update(self, update: "Update") -> Optional[Union[Tuple["Message", List[str]], Tuple["Message"]]]:
        if (
                update.message and
                update.message.text and
                len(update.message.text) > 1
        ):
            message = update.message
            args = message.text.split() # /command arg1 arg2 ...
            command = args[0]
            args = args[1:]
            if not (
                    message.text[0] == '/' and command in self.commands
            ):
                return None

            if self.check and not self.check.check_update(update):
                return None

            parameters = self._check_params_correct(args)
            if not parameters:
                return

            if not args:
                return (
                    message,
                )
            return message, *args
