import base64
import difflib
import requests

# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *
from aqt.sound import getAudio

from ._vendor.dragonmapper import hanzi


# TODO: load from config file
with open("API_KEY.txt", 'r') as api_key_file:
    API_KEY = api_key_file.read()


def test_pronunciation():
    # TODO: field should be configurable
    # TODO: rename stuff to be less Chinese specific
    hanzi = mw.reviewer.card.note()["Hanzi"]
    recorded_voice = getAudio(mw, False)
    tts_result = rest_request(recorded_voice)
    desired_pinyin = to_pinyin(hanzi)
    heard_pinyin = to_pinyin(tts_result)
    if desired_pinyin != heard_pinyin:
        showInfo("You were supposed to say: {}\n"
                 "{}\n"
                 "But Google heard you say: {}\n"
                 "{}\n"
                 "\n"
                 "<span style=\"font-size:x-large\">{}</span>".format(
            hanzi,
            desired_pinyin,
            tts_result,
            heard_pinyin,
            inline_diff(desired_pinyin, heard_pinyin)
        ), textFormat="rich")
    else:
        showInfo("Perfect. Google heard you say:\n"
                 "{}\n"
                 "{}".format(
            tts_result,
            heard_pinyin
        ))


def rest_request(audio_file_path):
    with open(audio_file_path, 'rb') as audio_content:
        encoded_audio = base64.b64encode(audio_content.read())

    payload = {
        "config": {
            "encoding": "ENCODING_UNSPECIFIED",
            "sampleRateHertz": "44100",
            # TODO: allow language to be configurable
            "languageCode": "zh-TW"
        },
        "audio": {
            "content": encoded_audio.decode("utf8")
        }
    }

    r = requests.post("https://speech.googleapis.com/v1/speech:recognize?key={}".format(API_KEY), json=payload)
    r.raise_for_status()
    data = r.json()
    transcript = ""
    for result in data["results"]:
        transcript += result["alternatives"][0]["transcript"].strip() + " "
    return transcript


# TODO: fix diff to parse from R to L (otherwise the accents are parsed weirdly), or just diff on Chinese
def inline_diff(a, b):
    matcher = difflib.SequenceMatcher(None, a, b)

    def process_tag(tag, i1, i2, j1, j2):
        if tag == 'replace':
            return f"<span style=\"color:red\">{matcher.b[j1:j2]}</span>"
            # return '[{}->{}]'.format(matcher.a[i1:i2], matcher.b[j1:j2])
        if tag == 'delete':
            return f"<span style=\"color:orange\">{matcher.a[i1:i2]}</span>"
        if tag == 'equal':
            return matcher.a[i1:i2]
        if tag == 'insert':
            return f"<span style=\"color:red\">{matcher.b[j1:j2]}</span>"
        assert False, "Unknown tag %r"%tag

    return ''.join(process_tag(*t) for t in matcher.get_opcodes())


def to_pinyin(sent):
    return hanzi.to_pinyin(sent, accented=False)


# create a new menu item, "test"
action = QAction("Check Pronunciation", mw)
# set it to call testFunction when it's clicked
action.triggered.connect(test_pronunciation)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
