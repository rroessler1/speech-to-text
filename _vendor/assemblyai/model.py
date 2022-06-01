"""Model module."""

import json

from assemblyai.config import ASSEMBLYAI_URL
from assemblyai.exceptions import handle_warnings
import requests


class Model(object):
    """Custom model object."""

    def __init__(self, client, phrases=None, name=None):
        self.headers = client.headers
        self.api = client.api
        self.phrases = phrases
        self.name = name
        self.id = None
        self.log = client.log
        self.status = None
        self.warning = None
        self.dict = None

    def __repr__(self):
        return 'Model(id=%s, status=%s)' % (self.id, self.status)

    def props(self):
        return [i for i in self.__dict__.keys() if i[:1] != '_']

    def reset(self, id=None):
        if id:
            self.id = id
            self.status = None
            self.name = None
            self.phrases = None
            self.warning = None
            self.dict = None

    def create(self):
        data = {}
        data["phrases"] = self.phrases  # TODO validate phrases
        if self.name:
            data['name'] = self.name
        payload = json.dumps(data)
        url = ASSEMBLYAI_URL + '/model'
        response = requests.post(url, data=payload, headers=self.headers)
        self.warning = handle_warnings(response, 'model', self.log)
        response = response.json()['model']
        self.id, self.status = response['id'], response['status']
        self.log.debug('Model %s %s' % (self.id, self.status))
        return self

    def get(self, id=None):
        """Get a custom model."""
        self.reset(id)
        url = ASSEMBLYAI_URL + '/model/' + str(self.id)
        response = requests.get(url, headers=self.headers)
        self.warning = handle_warnings(response, 'model', self.log)
        response = response.json()['model']
        # self.phrases = response['phrases']
        self.dict = response
        self.status = response['status']
        self.log.debug('Model %s %s' % (self.id, self.status))
        return self
