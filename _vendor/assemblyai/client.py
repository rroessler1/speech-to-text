"""Client module."""

import logging

from assemblyai.config import ASSEMBLYAI_URL, ASSEMBLYAI_TOKEN
# from assemblyai.exceptions import handle_warnings
from assemblyai.model import Model
from assemblyai.transcript import Transcript
# from assemblyai.token import trial_token, validate_token

logging.basicConfig()


class Client(object):
    """Client for the AssemblyAI API."""

    def __init__(self, token=None, debug=False):
        """Initialize client."""
        self.token = token or ASSEMBLYAI_TOKEN  # or trial_token()
        # validate_token(self.token)
        self.headers = {'authorization': self.token}
        self.api = ASSEMBLYAI_URL

        self.log = logging.getLogger('AssemblyAI')
        if debug:
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.ERROR)

        self.model = Model(self)
        self.transcript = Transcript(self)

    def __repr__(self):
        concat_token = self.token[0:8] + '..'
        return 'Client(token=%s)' % concat_token

    def train(self, phrases, name=None):
        """Create a custom model."""
        client = self
        model = Model(client, phrases=phrases, name=name)
        model = model.create()
        return model

    def transcribe(self, filename=None, audio_url=None, model=None,
                   speaker_count=None, format_text=True):
        """Create a transcript request. If the transcript depends on a
        custom model, defer creation until model is trained."""
        client = self
        transcript = Transcript(client, filename=filename,
                                audio_url=audio_url, model=model,
                                speaker_count=speaker_count,
                                format_text=format_text)
        transcript = transcript.create()
        return transcript
