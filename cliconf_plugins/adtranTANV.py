# Copyright: (c) 2018, Ansible Project
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
author: Unknown (!UNKNOWN)
name: adtranTANV
short_description: Use AdTran TotalAccess/NetVanta cliconf to run commands on AdTran platform
description:
  - This AdTran TotalAccess/NetVanta plugin provides low level abstraction APIs for
    sending and receiving CLI commands from AdTran network devices.
'''

import re
import json

from itertools import chain

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_text
from ansible.module_utils.common._collections_compat import Mapping
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import to_list
from ansible.plugins.cliconf import CliconfBase


class Cliconf(CliconfBase):

    def get_device_info(self):
        device_info = {}

        device_info['network_os'] = 'adtranTANV'
        reply = self.get('show version')
        data = to_text(reply, errors='surrogate_or_strict').strip()

        match = re.search(r'OS version\s(\S+)', data)
        if match:
            device_info['network_os_version'] = match.group(1)

        match = re.search(r'Platform:\s([^,]+)', data)
        if match:
            device_info['network_os_model'] = match.group(1)

        # reply = self.get('show host name')
        # device_info['network_os_hostname'] = to_text(reply, errors='surrogate_or_strict').strip()

        reply = self.get('show running-config | include hostname')
        data = to_text(reply, errors='surrogate_or_strict').strip()
        match = re.search(r'hostname "([^"]+)', data)
        if match:
            device_info['network_os_hostname'] = match.group(1)

        return device_info

    def get_config(self, source='running', flags=None):
        if source not in ('running', 'startup'):
            raise ValueError("fetching configuration from %s is not supported" % source)

        if source == 'running':
            cmd = 'show running-config '
        else:
            cmd = 'show startup-config'

        if flags:
            cmd += ' '.join(to_list(flags))
            cmd = cmd.strip()

        return self.send_command(cmd)

    #def edit_config(self, candidate=None, commit=True, replace=False, comment=None):
    #    for cmd in chain(['configure'], to_list(candidate)):
    #        self.send_command('configure terminal')

    #@enable_mode
    def edit_config(self, commands):
        resp = {}

        results = []
        requests = []
        self.send_command('configure')
        for line in to_list(commands):
            if not isinstance(line, Mapping):
                line = {'command': line}

            cmd = line['command']
            if cmd != 'end' and cmd[0] != '!':
                results.append(self.send_command(**line))
                requests.append(cmd)

        self.send_command('end')

        resp['request'] = requests
        resp['response'] = results
        return resp

    # def get(self, command=None, prompt=None, answer=None, sendonly=False, newline=True, output=None, check_all=False):
    #     if not command:
    #         raise ValueError('must provide value of command to execute')
    #     if output:
    #         raise ValueError("'output' value %s is not supported for get" % output)

    #     return self.send_command(command=command, prompt=prompt, answer=answer, sendonly=sendonly, newline=newline, check_all=check_all)

    def get(self, command, prompt=None, answer=None, sendonly=False, newline=True, check_all=False):
        return self.send_command(command=command, prompt=prompt, answer=answer, sendonly=sendonly, newline=newline, check_all=check_all)

    # def commit(self, comment=None):
    #     if comment:
    #         command = 'commit comment "{0}"'.format(comment)
    #     else:
    #         command = 'commit'
    #     self.send_command(command)

    # def discard_changes(self, *args, **kwargs):
    #     self.send_command('exit discard')

    def run_commands(self, commands=None, check_rc=True):
        if commands is None:
            raise ValueError("'commands' value is required")

        responses = list()
        for cmd in to_list(commands):
            if not isinstance(cmd, Mapping):
                cmd = {'command': cmd}

            output = cmd.pop('output', None)
            if output:
                raise ValueError("'output' value %s is not supported for run_commands" % output)

            try:
                out = self.send_command(**cmd)
            except AnsibleConnectionFailure as e:
                if check_rc:
                    raise
                out = getattr(e, 'err', e)

            responses.append(out)

        return responses

    # def get_device_operations(self):
    #     return {
    #         'supports_diff_replace': False,
    #         'supports_commit': True,
    #         'supports_rollback': False,
    #         'supports_defaults': False,
    #         'supports_onbox_diff': False,
    #         'supports_commit_comment': True,
    #         'supports_multiline_delimiter': False,
    #         'supports_diff_match': False,
    #         'supports_diff_ignore_lines': False,
    #         'supports_generate_diff': False,
    #         'supports_replace': False
    #     }

    def get_capabilities(self):
        result = super(Cliconf, self).get_capabilities()
        result['rpc'] += ['commit', 'discard_changes', 'run_commands']
        # result['device_operations'] = self.get_device_operations()
        return json.dumps(result)
