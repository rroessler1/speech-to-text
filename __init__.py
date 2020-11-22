import sys
sys.path.insert(0, "/home/ross/tts/lib/python3.8/site-packages")
sys.path.insert(0, '/home/ross/tts/lib/python38.zip')
sys.path.insert(0, "/home/ross/tts/lib/python3.8/")
sys.path.insert(0, "/home/ross/tts/lib/python3.8/lib-dynload")

import base64
import requests

# import the main window object (mw) from aqt
from aqt import mw
from aqt import gui_hooks
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *
from aqt.sound import getAudio

from myaddon import pinyintools
from myaddon import diff


with open("API_KEY.txt", 'r') as api_key_file:
    API_KEY = api_key_file.read()

# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

def testFunction():
    showInfo("<span style=\"font-size:x-large\">" + diff.inline_diff("this is one two sentence", "these are sentences") + "</span>", textFormat="rich")
    # showInfo("<b>Card count:</b> \nCard:\n{}\nQ:\nID:\n{}".format(mw.reviewer.card, mw.reviewer.card.note()["Hanzi"]), textFormat="rich")


def test_pronunciation():
    hanzi = mw.reviewer.card.note()["Hanzi"]
    recorded_voice = getAudio(mw, False)
    tts_result = rest_request(recorded_voice)
    desired_pinyin = pinyintools.to_pinyin(hanzi)
    heard_pinyin = pinyintools.to_pinyin(tts_result)
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
            diff.inline_diff(desired_pinyin, heard_pinyin)
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
            "languageCode": "zh-TW"
        },
        "audio": {
            "content": encoded_audio.decode("utf8")
        }
    }
    #
    # payload = {
    #     "config": {
    #         "encoding": "FLAC",
    #         "sampleRateHertz": 16000,
    #         "languageCode": "en-US",
    #         "enableWordTimeOffsets": False
    #     },
    #     "audio": {
    #         "uri": "gs://cloud-samples-tests/speech/brooklyn.flac"
    #     }
    # }


    headers = {}
    # if sha1(options['key'].encode("utf-8")).hexdigest() == "8224a632410a845cbb4b20f9aef131b495f7ad7f":
    #     headers['x-origin'] = 'https://explorer.apis.google.com'
    #
    # if options['profile'] != 'default':
    #     payload["audioConfig"]["effectsProfileId"] = [options['profile']]

    r = requests.post("https://speech.googleapis.com/v1/speech:recognize?key={}".format(API_KEY), headers=headers, json=payload)
    r.raise_for_status()

    data = r.json()
    transcript = ""
    for result in data["results"]:
        transcript += result["alternatives"][0]["transcript"].strip() + " "
    return transcript


# create a new menu item, "test"
action = QAction("test", mw)
# set it to call testFunction when it's clicked
action.triggered.connect(test_pronunciation)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
