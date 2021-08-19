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

class File:
    def __init__(self, path: str, filename: str, version: str):
        self._path = path
        self._filename = filename
        self._version = version
        self._class_name = None

    @property
    def full_file_path(self):
        return self._path + self._filename

    @property
    def filename(self):
        return self._filename

    @property
    def version(self):
        return self._version

    @property
    def class_name(self):
        return self._class_name

    @class_name.setter
    def class_name(self, value):
        self._class_name = value

    def __str__(self):
        return f'{self._path}{self._filename}'
