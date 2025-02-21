# Copyright: (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import re

from ansible.plugins.terminal import TerminalBase
from ansible.errors import AnsibleConnectionFailure


class TerminalModule(TerminalBase):

    terminal_stdout_re = [
	# Multiple lines that don't start with a % and ends with the prompt
        #re.compile(br"^[^%].*[\w+\-\.:@\/\[\]]+(?:\([^\)]+\)){,3}(?:>|#) ?$", re.M | re.S),
        re.compile(br"[\r\n]?[\w+\-\.:@\/\[\]]+(?:\([^\)]+\)){,3}(?:>|#) ?$"),
        #re.compile(br".*[\r\n]?[\w+\-\.:\/\[\]\s]+\?\[y\\n\] ?$"),

	# If you want y/n questions excluded (consumed) from the output
	#re.compile(br"Reload scheduled in .*\?\[y\/n\] ?$", re.M | re.S),
        #re.compile(br"\?\[y\/n\] ?$"),
        #re.compile(br"\@[\w\-\.]+:\S+?[>#\$] ?$")
    ]

    terminal_stderr_re = [
        re.compile(br"\n%")
    ]


    terminal_length = os.getenv('ANSIBLE_ADTRANTANV_TERMINAL_LENGTH', 0)

    def on_open_shell(self):
        try:
            self._exec_cli_command('terminal length %s' % self.terminal_length)
        except AnsibleConnectionFailure:
            raise AnsibleConnectionFailure('unable to set terminal parameters')
