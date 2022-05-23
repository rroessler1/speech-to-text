"""Transcript module."""

import json

from assemblyai.exceptions import handle_warnings
import requests


class Transcript(object):
    """Transcript object."""

    def __init__(self, client, filename=None, audio_url=None, model=None,
                 speaker_count=None, format_text=True):
        self.api = client.api
        self.audio_url = audio_url
        self.confidence = None
        self.dict = None
        self.filename = filename
        self.headers = client.headers
        self.id = None
        self.log = client.log
        self.model = model
        self.segments = None
        self.speaker_count = speaker_count
        self.status = None
        self.text = None
        self.warning = None
        self.format_text = format_text

    def __repr__(self):
        return 'Transcript(id=%s, status=%s, text=%s)' % (
            self.id, self.status, self.text)

    def props(self):
        return [i for i in self.__dict__.keys() if i[:1] != '_']

    def reset(self, id=None):
        if id:
            # self.api = client.api
            self.audio_url = None
            self.confidence = None
            self.dict = None
            self.filename = None
            # self.headers = client.headers
            self.id = id
            self.model = None
            self.segments = None
            self.speaker_count = None
            self.status = None
            self.text = None
            self.warning = None
            self.format_text = True

    def validate(self):
        """Deconflict filename and audio_url."""
        if self.filename and not self.audio_url:
            if self.filename.startswith('http'):
                self.audio_url = self.filename
                self.filename = None
            else:
                self.audio_url = self.upload(self.filename)

    def create(self):
        """Create a transcript."""
        # TODO remove model checking after api defaults to waiting for models
        self.log.debug("validating create()")
        self.validate()
        self.log.debug("validation complete")
        if self.model:
            self.model = self.model.get()
        if self.model and self.model.status != 'trained':
            self.status = 'waiting for model'
        else:
            data = {}
            data['audio_src_url'] = self.audio_url
            if self.model:
                data['model_id'] = self.model.id
            if self.speaker_count:
                data['speaker_count'] = self.speaker_count
            if not self.format_text:
                data['options'] = {'format_text': self.format_text}
            payload = json.dumps(data)
            url = self.api + '/transcript'
            self.log.debug("posting transcript")
            response = requests.post(url, data=payload, headers=self.headers)
            self.log.debug("transcript posted")
            self.warning = handle_warnings(response, 'transcript', self.log)
            response = response.json()['transcript']
            self.id, self.status = response['id'], response['status']
            self.log.debug('Transcript %s %s' % (self.id, self.status))
        return self

    def check_model(self):
        # TODO remove model checking after api defaults to waiting for models
        self.model = self.model.get()
        if self.model.status == 'trained' and not self.id:
            self = self.create()
        elif self.model.status != 'trained':
            self.status = 'waiting for model'

    def request(self):
        url = self.api + '/transcript/' + str(self.id)
        response = requests.get(url, headers=self.headers)
        self.warning = handle_warnings(response, 'transcript', self.log)
        response = response.json()['transcript']
        return response

    def get(self, id=None):
        """Get a transcript."""
        self.reset(id)
        if self.model:
            self.check_model()
        if self.id:
            response = self.request()
            self.dict = response
            self.id, self.status = response['id'], response['status']
            self.text = response['text']
            self.confidence = response['confidence']
            self.segments = response['segments']
            self.speaker_count = response['speaker_count']
            if 'options' in response and 'format_text' in response['options']:
                self.format_text = response['options']['format_text']
        self.log.debug('Transcript %s %s' % (self.id, self.status))
        return self

    def upload(self, filepath):
        """Upload a file."""
        upload_url = 'https://api.assemblyai.com/upload'
        presigned_url = requests.post(upload_url, headers=self.headers).text
        self.log.debug(presigned_url)
        url = presigned_url.split('?')[0]
        with open(filepath, 'rb') as f:
            r = requests.put(presigned_url, data=f.read())
        r.raise_for_status()
        self.log.debug("upload complete to %s" % url)
        return url
