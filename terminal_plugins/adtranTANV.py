# Copyright: (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json
import re

from ansible.module_utils._text import to_text, to_bytes
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

    def on_become(self, passwd=None):
        prompt = self._get_prompt()
        if prompt and prompt.endswith(b'#'):
            return

        cmd = {u'command': u'enable'}
        if passwd:
            cmd[u'prompt'] = to_text(r"[\r\n]?[Pp]assword: ?$", errors='surrogate_or_strict')
            cmd[u'answer'] = passwd
        try:
            self._exec_cli_command(to_bytes(json.dumps(cmd), errors='surrogate_or_strict'))
            prompt = self._get_prompt()
            if prompt is None or not prompt.endswith(b'#'):
                raise AnsibleConnectionFailure('failed to elevate privilege to enable mode still at prompt [%s]' % prompt)

            cmd = {u'command': u'terminal length 0'}
            self._exec_cli_command(to_bytes(json.dumps(cmd), errors='surrogate_or_strict'))
            prompt = self._get_prompt()
            if prompt is None or not prompt.endswith(b'#'):
                raise AnsibleConnectionFailure('failed to setup terminal in enable mode')

        except AnsibleConnectionFailure as e:
            prompt = self._get_prompt()
            raise AnsibleConnectionFailure('unable to elevate privilege to enable mode, at prompt [%s] with error: %s' % (prompt, e.message))

    def on_unbecome(self):
        prompt = self._get_prompt()
        if prompt is None:
            # if prompt is None most likely the terminal is hung up at a prompt
            return

        if b'(config' in prompt:
            self._exec_cli_command(b'end')
            self._exec_cli_command(b'disable')

        elif prompt.endswith(b'#'):
            self._exec_cli_command(b'disable')