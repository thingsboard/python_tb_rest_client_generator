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

from json import dumps
from time import time, sleep

from requests import post
from threading import Thread
from logging import getLogger

from tb_rest_client.api.api_ce import *
from tb_rest_client.models.models_ce import *
from tb_rest_client.models.models_pe import *
from tb_rest_client.configuration import Configuration
from tb_rest_client.api_client import ApiClient

logger = getLogger(__name__)


class RestClientBase(Thread):
    def __init__(self, base_url):
        super().__init__()
        if base_url.startswith("http"):
            self.base_url = base_url
        else:
            self.base_url = "http://" + base_url
        self.token_info = {"token": "", "refreshToken": 0}
        self.api_client = None
        self.username = None
        self.password = None
        self.logged_in = False
        self.stopped = True
        self.configuration = Configuration()
        self.configuration.host = self.base_url

    def run(self):
        self.stopped = False
        while not self.stopped:
            try:
                check_time = time()
                if check_time >= self.token_info["refreshToken"] and self.logged_in:
                    if self.username and self.password:
                        self.login(self.username, self.password)
                    else:
                        logger.error("No username or password provided!")
                sleep(1)
            except Exception as e:
                logger.exception(e)
                break
            except KeyboardInterrupt:
                break

    def stop(self):
        self.stopped = True

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def login(self, username, password):
        """Authorization on the host and saving the toke information"""
        if self.username is None and self.password is None:
            self.username = username
            self.password = password
            self.logged_in = True

        token_json = post(self.base_url + "/api/auth/login", json={"username": username, "password": password},
                          verify=self.configuration.verify_ssl).json()
        token = None
        if isinstance(token_json, dict) and token_json.get("token") is not None:
            token = token_json["token"]
        self.configuration.api_key_prefix["X-Authorization"] = "Bearer"
        self.configuration.api_key["X-Authorization"] = token

        self.api_client = ApiClient(self.configuration)
        self.__load_controllers()

    def get_token(self):
        return self.token_info["token"]
