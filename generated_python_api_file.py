# coding: utf-8
#      Copyright 2020. ThingsBoard
#  #
#      Licensed under the Apache License, Version 2.0 (the "License");
#      you may not use this file except in compliance with the License.
#      You may obtain a copy of the License at
#  #
#          http://www.apache.org/licenses/LICENSE-2.0
#  #
#      Unless required by applicable law or agreed to in writing, software
#      distributed under the License is distributed on an "AS IS" BASIS,
#      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#      See the License for the specific language governing permissions and
#      limitations under the License.
#

from re import sub


class GeneratedPythonApiFile:
    def __init__(self, name: str, have_init_section: bool):
        self._name = name
        self._have_init_section = have_init_section
        self._top_section = ''
        self._methods_section = ''
        self._bot_section = ''
        self._init: [str] = [] if self._have_init_section else None
        self._fill_top_section()
        self._fill_bot_section()

    @staticmethod
    def _read_file(path):
        with open(path, 'r') as f:
            data = f.readlines()
        return ''.join(data)

    def _fill_top_section(self):
        if self._name == 'RestClientBase':
            self._top_section += self._read_file('config/rest_client_base_top.py')
        elif self._name == 'RestClientCE':
            self._top_section += self._read_file('config/rest_client_ce_top.py')
        else:
            self._top_section += self._read_file('config/rest_client_pe_top.py')

    def _fill_bot_section(self):
        if self._name == 'RestClientBase' or self._name == 'RestClientPe':
            self._bot_section += self._read_file('config/rest_client_base_bot.py')

    def _generate_load_controllers_function(self) -> str:
        result = ''

        if self._have_init_section:
            result = '    def __load_controllers(self):\n'
            for cnt in set(self._init):
                result += '        self.' + '_'.join(sub(r'(?<!^)(?=[A-Z])', '_', cnt.__name__).lower().split('_')[
                                                     :-1]) + ' = ' + cnt.__name__ + '(self.api_client)\n'

        return result

    def generate_file(self) -> str:
        init_section = self._generate_load_controllers_function()
        return self._top_section + '\n' + self._methods_section + '\n' + init_section + '\n' + self._bot_section

    @property
    def methods_section(self):
        return self._methods_section

    @methods_section.setter
    def methods_section(self, value):
        self._methods_section += value

    @property
    def init(self):
        return self._init

    @init.setter
    def init(self, value):
        self._init.append(value)
