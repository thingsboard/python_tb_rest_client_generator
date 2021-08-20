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
import re


class Function:
    def __init__(self, function_name: str, controller: str, params: [str]):
        self._function_name = function_name
        self._controller_name = '_'.join(controller.split('_')[0:-1])
        self._params = {x.split(': ')[0].split(' ')[1] + '|' + x.split(' ')[-1][1:-1]: (
            x.split(': ')[0].split(' ')[0] if '_id' not in x.split(': ')[0].split(' ')[1] else
            x.split(': ')[0].split(' ')[1].title().replace('_', '')) for x in params}
        self._check_params()
        self._str_function = self._function_to_str()

    def _check_params(self):
        if self._params.get('object)|eviceWithDeviceCredential'):
            self._params.pop('object)|eviceWithDeviceCredential')
            self._params['object'] = '{}'

        print(self._params)

        for key, val in self._params.items():
            if val == 'ResourceId' or val == 'FromId' or val == 'ToId' or val == 'ClientRegistrationTemplateId' or val == 'UserGroupId' or val == 'SolutionTemplateId':
                self._params[key] = 'EntityId'
            elif 'Ids' in val:
                self._params[key] = 'list'
            elif val == 'Object':
                self._params[key] = 'dict'
            elif val == 'SubCustomerId':
                self._params[key] = 'CustomerId'
            elif val == 'OwnerId':
                self._params[key] = 'UserId'
            elif val == 'GroupId':
                self._params[key] = 'EntityGroupId'

    def _function_to_str(self) -> str:
        result = '    def '
        match = re.search(r'\d+$', self._function_name)
        result += ('' if 'integration' not in self._controller_name else '_'.join(
            self._controller_name.split('_')[:-2]) + '_') + '_'.join(self._function_name.split('_')[0:-2]) + (
                      '' if not match else '_v' + match.group()) + (
                      '' if 'integration' not in self._controller_name and self._controller_name != 'event_controller' else '_' +
                                                                                                                            self._function_name.split(
                                                                                                                                '_')[
                                                                                                                                -1]) + '(' + 'self, ' + ', '.join(
            [(x.split('|')[0] + ': ' + y if 'required' in x else x.split('|')[0] + '=None') for x, y in self._params.items()]) + ')' + ':\n'

        for k, v in self._params.items():
            if '_id' in k and '_ids' not in k:
                result += '        ' + k.split('|')[0] + ' = self.get_id(' + k.split('|')[0] + ')\n'

        result += '        return self.' + self._controller_name + '.' + self._function_name + '(' + ', '.join(
            [x.split('|')[0] + '=' + x.split('|')[0] for x, _ in self._params.items()]) + ')\n'

        return result

    @property
    def str_function(self):
        return self._str_function

    @property
    def params(self):
        return self._params

    @property
    def name(self):
        return self._function_name

    def __str__(self):
        return f'{self._function_name} {self._params}'
