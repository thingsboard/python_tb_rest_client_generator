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

from tb_rest_client.rest_client_base import *

from tb_rest_client.api.api_ce import *
from tb_rest_client.api.api_pe import *
from tb_rest_client.models.models_pe import *

logger = getLogger(__name__)


class RestClientPE(RestClientBase):
    def __init__(self, base_url):
        super().__init__(base_url)

    def login(self, username, password):
        super(RestClientPE, self).login(username=username, password=password)
        self.__load_controllers()
