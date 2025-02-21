#
# This is a merge of settings from ciscosmb.py and functions from edgeswitch.py
# ~/.ansible/collections/ansible_collections/community/ciscosmb/plugins/terminal/ciscosmb.py
# /usr/lib/python3/dist-packages/ansible_collections/community/network/plugins/terminal/edgeswitch.py
#
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import re

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_text, to_bytes
from ansible.plugins.terminal import TerminalBase


class TerminalModule(TerminalBase):

    # https://docs.ansible.com/ansible/latest/collections/ansible/netcommon/network_cli_connection.html
    #terminal_stdout_re = [
    #    re.compile(br"\(([^\(\)]+)\) [>#]$"),
    #    re.compile(br"\(([^\(\)]+)\) \(([^\(\)]+)\)#$")
    #]

    terminal_stdout_re = [
        re.compile(br"[\r\n]?[\w\+\-\.:\/\[\]]+(?:\([^\)]+\)){0,3}(?:[>#]) ?$")
    ]

    terminal_stderr_re = [
        re.compile(br"% ?Error"),
        re.compile(br"^% \w+", re.M),
        re.compile(br"% ?Bad secret"),
        re.compile(br"[\r\n%] Bad passwords"),
        re.compile(br"invalid input", re.I),
        re.compile(br"(?:incomplete|ambiguous) command", re.I),
        re.compile(br"connection timed out", re.I),
        re.compile(br"[^\r\n]+ not found"),
        re.compile(br"'[^']' +returned error code: ?\d+"),
        re.compile(br"Bad mask", re.I),
        re.compile(br"% ?(\S+) ?overlaps with ?(\S+)", re.I),
        re.compile(br"[%\S] ?Error: ?[\s]+", re.I),
        re.compile(br"[%\S] ?Informational: ?[\s]+", re.I),
        re.compile(br"Command authorization failed"),
    ]

    def on_open_shell(self):
        try:
            self._exec_cli_command(b"terminal datadump")
        except AnsibleConnectionFailure as e:
            raise_from(AnsibleConnectionFailure("unable to set terminal parameters"), e)

        try:
            self._exec_cli_command(b"terminal width 0")
        except AnsibleConnectionFailure:
            display.display(
                "WARNING: Unable to set terminal width, command responses may be truncated"
            )

        try:
            self._exec_cli_command(b"terminal no prompt")
        except AnsibleConnectionFailure:
            display.display(
                "WARNING: Unable disable prompt, command responses may fail"
            )

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
            self._exec_cli_command(b'exit')

        elif prompt.endswith(b'#'):
            self._exec_cli_command(b'exit')
