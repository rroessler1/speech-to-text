import base64
import difflib
import re
import requests
from unicodedata import category

# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *
from aqt.sound import getAudio

from ._vendor.dragonmapper import hanzi


# Constants:
WINDOW_NAME = "Test Your Pronunciation"
SETTINGS_ORGANIZATION = "github_rroessler1"
SETTINGS_APPLICATION = "stt-anki-plugin"
API_KEY_SETTING_NAME = "google-stt-api-key"
FIELD_TO_READ_SETTING_NAME = "field-to-read"
FIELD_TO_READ_DEFAULT_NAME = "Front"
LANGUAGE_SETTING_NAME = "language-name"
CHINESE_LANGUAGE_CODES = {'zh-TW', 'zh', 'yue-Hant-HK', 'cmn-Hans-CN', 'cmn-Hant-TW'}
LANGUAGES_WITHOUT_SPACES = {
    # Chinese
    'zh-TW', 'zh', 'yue-Hant-HK', 'cmn-Hans-CN', 'cmn-Hant-TW',
    # Japanese
    'ja-JP',
    # Lao, Thai, Burmese, Khmer
    'lo-LA', 'th-TH', 'my-MM', 'km-KH'
}
SUPPORTED_LANGUAGE_CODES = ['af-ZA', 'sq-AL', 'am-ET', 'ar-DZ', 'ar-BH', 'ar-EG', 'ar-IQ', 'ar-IL', 'ar-JO', 'ar-KW', 'ar-LB', 'ar-MA', 'ar-OM', 'ar-QA', 'ar-SA', 'ar-PS', 'ar-TN', 'ar-AE', 'ar-YE', 'hy-AM', 'az-AZ', 'eu-ES', 'bn-BD', 'bn-IN', 'bs-BA', 'bg-BG', 'my-MM', 'ca-ES', 'yue-Hant-HK', 'zh', 'zh-TW', 'hr-HR', 'cs-CZ', 'da-DK', 'nl-BE', 'nl-NL', 'en-AU', 'en-CA', 'en-GH', 'en-HK', 'en-IN', 'en-IE', 'en-KE', 'en-NZ', 'en-NG', 'en-PK', 'en-PH', 'en-SG', 'en-ZA', 'en-TZ', 'en-GB', 'en-US', 'et-EE', 'fil-PH', 'fi-FI', 'fr-BE', 'fr-CA', 'fr-FR', 'fr-CH', 'gl-ES', 'ka-GE', 'de-AT', 'de-DE', 'de-CH', 'el-GR', 'gu-IN', 'iw-IL', 'hi-IN', 'hu-HU', 'is-IS', 'id-ID', 'it-IT', 'it-CH', 'ja-JP', 'jv-ID', 'kn-IN', 'km-KH', 'ko-KR', 'lo-LA', 'lv-LV', 'lt-LT', 'mk-MK', 'ms-MY', 'ml-IN', 'mr-IN', 'mn-MN', 'ne-NP', 'no-NO', 'fa-IR', 'pl-PL', 'pt-BR', 'pt-PT', 'pa-Guru-IN', 'ro-RO', 'ru-RU', 'sr-RS', 'si-LK', 'sk-SK', 'sl-SI', 'es-AR', 'es-BO', 'es-CL', 'es-CO', 'es-CR', 'es-DO', 'es-EC', 'es-SV', 'es-GT', 'es-HN', 'es-MX', 'es-NI', 'es-PA', 'es-PY', 'es-PE', 'es-PR', 'es-ES', 'es-US', 'es-UY', 'es-VE', 'su-ID', 'sw-KE', 'sw-TZ', 'sv-SE', 'ta-IN', 'ta-MY', 'ta-SG', 'ta-LK', 'te-IN', 'th-TH', 'tr-TR', 'uk-UA', 'ur-IN', 'ur-PK', 'uz-UZ', 'vi-VN', 'zu-ZA']
SUPPORTED_LANGUAGE_NAMES = ['Afrikaans (South Africa)', 'Albanian (Albania)', 'Amharic (Ethiopia)', 'Arabic (Algeria)', 'Arabic (Bahrain)', 'Arabic (Egypt)', 'Arabic (Iraq)', 'Arabic (Israel)', 'Arabic (Jordan)', 'Arabic (Kuwait)', 'Arabic (Lebanon)', 'Arabic (Morocco)', 'Arabic (Oman)', 'Arabic (Qatar)', 'Arabic (Saudi Arabia)', 'Arabic (State of Palestine)', 'Arabic (Tunisia)', 'Arabic (United Arab Emirates)', 'Arabic (Yemen)', 'Armenian (Armenia)', 'Azerbaijani (Azerbaijan)', 'Basque (Spain)', 'Bengali (Bangladesh)', 'Bengali (India)', 'Bosnian (Bosnia and Herzegovina)', 'Bulgarian (Bulgaria)', 'Burmese (Myanmar)', 'Catalan (Spain)', 'Chinese, Cantonese (Traditional Hong Kong)', 'Chinese, Mandarin (Simplified, China)', 'Chinese, Mandarin (Traditional, Taiwan)', 'Croatian (Croatia)', 'Czech (Czech Republic)', 'Danish (Denmark)', 'Dutch (Belgium)', 'Dutch (Netherlands)', 'English (Australia)', 'English (Canada)', 'English (Ghana)', 'English (Hong Kong)', 'English (India)', 'English (Ireland)', 'English (Kenya)', 'English (New Zealand)', 'English (Nigeria)', 'English (Pakistan)', 'English (Philippines)', 'English (Singapore)', 'English (South Africa)', 'English (Tanzania)', 'English (United Kingdom)', 'English (United States)', 'Estonian (Estonia)', 'Filipino (Philippines)', 'Finnish (Finland)', 'French (Belgium)', 'French (Canada)', 'French (France)', 'French (Switzerland)', 'Galician (Spain)', 'Georgian (Georgia)', 'German (Austria)', 'German (Germany)', 'German (Switzerland)', 'Greek (Greece)', 'Gujarati (India)', 'Hebrew (Israel)', 'Hindi (India)', 'Hungarian (Hungary)', 'Icelandic (Iceland)', 'Indonesian (Indonesia)', 'Italian (Italy)', 'Italian (Switzerland)', 'Japanese (Japan)', 'Javanese (Indonesia)', 'Kannada (India)', 'Khmer (Cambodia)', 'Korean (South Korea)', 'Lao (Laos)', 'Latvian (Latvia)', 'Lithuanian (Lithuania)', 'Macedonian (North Macedonia)', 'Malay (Malaysia)', 'Malayalam (India)', 'Marathi (India)', 'Mongolian (Mongolia)', 'Nepali (Nepal)', 'Norwegian Bokmål (Norway)', 'Persian (Iran)', 'Polish (Poland)', 'Portuguese (Brazil)', 'Portuguese (Portugal)', 'Punjabi (Gurmukhi India)', 'Romanian (Romania)', 'Russian (Russia)', 'Serbian (Serbia)', 'Sinhala (Sri Lanka)', 'Slovak (Slovakia)', 'Slovenian (Slovenia)', 'Spanish (Argentina)', 'Spanish (Bolivia)', 'Spanish (Chile)', 'Spanish (Colombia)', 'Spanish (Costa Rica)', 'Spanish (Dominican Republic)', 'Spanish (Ecuador)', 'Spanish (El Salvador)', 'Spanish (Guatemala)', 'Spanish (Honduras)', 'Spanish (Mexico)', 'Spanish (Nicaragua)', 'Spanish (Panama)', 'Spanish (Paraguay)', 'Spanish (Peru)', 'Spanish (Puerto Rico)', 'Spanish (Spain)', 'Spanish (United States)', 'Spanish (Uruguay)', 'Spanish (Venezuela)', 'Sundanese (Indonesia)', 'Swahili (Kenya)', 'Swahili (Tanzania)', 'Swedish (Sweden)', 'Tamil (India)', 'Tamil (Malaysia)', 'Tamil (Singapore)', 'Tamil (Sri Lanka)', 'Telugu (India)', 'Thai (Thailand)', 'Turkish (Turkey)', 'Ukrainian (Ukraine)', 'Urdu (India)', 'Urdu (Pakistan)', 'Uzbek (Uzbekistan)', 'Vietnamese (Vietnam)', 'Zulu (South Africa)']

PUNCTUATION_TABLE = dict.fromkeys(i for i in range(sys.maxunicode) if category(chr(i)).startswith('P'))
REMOVE_HTML_RE = re.compile('<[^<]+?>')

class IgnorableError(Exception):
    pass


def settings_dialog():
    SettingsDialog(app_settings, mw).show()


def test_pronunciation():
    api_key = app_settings.value(API_KEY_SETTING_NAME, "", type=str)
    field_to_read = app_settings.value(FIELD_TO_READ_SETTING_NAME, FIELD_TO_READ_DEFAULT_NAME, type=str)
    language_code = SUPPORTED_LANGUAGE_CODES[SUPPORTED_LANGUAGE_NAMES.index(app_settings.value(LANGUAGE_SETTING_NAME, 'English (United States)', type=str))]
    if api_key == '' or not mw.reviewer.card:
        settings_dialog()
        return
    if field_to_read not in mw.reviewer.card.note():
        show_error_dialog(f'This plugin needs to know which field you are reading. '
                                 f'It\'s looking for a field named: "{field_to_read}", '
                                 f'but there is no field named: "{field_to_read}" on the current card. '
                                 f'Please check the settings.',
                          True)
        return

    to_read_text = mw.reviewer.card.note()[field_to_read]
    to_read_text = strip_all_punc(remove_html(to_read_text)).strip()
    # This stores the file as "rec.wav" in the User's media collection.
    # It will overwrite the file every time, so there's no need to delete it after.
    recorded_voice = getAudio(mw, False)
    # If the user canceled the recording, do nothing and return
    if not recorded_voice:
        return
    try:
        tts_result = rest_request(recorded_voice, api_key, language_code)
        tts_result = strip_all_punc(tts_result).strip()
    except IgnorableError:
        return
    except requests.exceptions.ConnectionError as err:
        show_error_dialog(f"ConnectionError, could not access the Google Speech-to-Text service.\nError: {err}")
        return

    # idea: either completely remove all punctuation for both sentences, or remove it from beginning and end of words
    # for space-segmented languages
    # pros: overall better diff accuracy and more likely to report to user as correct
    # cons: might make diff look slightly weirder due to lack of punctuation
    # cons of first method specifically: with things like "dont" or "crosscountry"
    if to_read_text.lower() != tts_result.lower():
        # TODO: add window title
        if language_code in CHINESE_LANGUAGE_CODES:
            to_read_text_pinyin = to_pinyin(to_read_text)
            heard_pinyin = to_pinyin(tts_result)
            showInfo("You were supposed to say:<br/>{}<br/>{}<br/>"
                     "But the computer heard you say:<br/>{}<br/>{}<br/><br/>"
                     "<span style=\"font-size:x-large\">{}</span><br/>".format(
                to_read_text,
                to_read_text_pinyin,
                tts_result,
                heard_pinyin,
                inline_diff(to_read_text, tts_result, True)
            ), textFormat="rich")
        else:
            diff1 = to_read_text.lower() if language_code in LANGUAGES_WITHOUT_SPACES else to_read_text.lower().split()
            diff2 = tts_result.lower() if language_code in LANGUAGES_WITHOUT_SPACES else tts_result.lower().split()
            showInfo("You were supposed to say:<br/>{}<br/>"
                     "But the computer heard you say:<br/>{}<br/><br/>"
                     "<span style=\"font-size:x-large\">{}</span><br/>".format(
                to_read_text,
                tts_result,
                inline_diff(diff1, diff2)
            ), textFormat="rich")
    else:
        showInfo("Correct! The computer heard you say:<br/>{}".format(tts_result))


def rest_request(audio_file_path, api_key, language_code):
    with open(audio_file_path, 'rb') as audio_content:
        encoded_audio = base64.b64encode(audio_content.read())

    payload = {
        "config": {
            "encoding": "ENCODING_UNSPECIFIED",
            "sampleRateHertz": "44100",
            "languageCode": language_code
        },
        "audio": {
            "content": encoded_audio.decode("utf8")
        }
    }

    r = requests.post("https://speech.googleapis.com/v1/speech:recognize?key={}".format(api_key), json=payload)
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        if r.status_code == 400:
            show_error_dialog('Received a 400 Error code; your API key is probably invalid.', True)
            raise IgnorableError
        # otherwise re-throw the exception
        raise
    data = r.json()
    if "results" not in data:
        show_error_dialog('No results from Google Speech-to-Text service; maybe your audio recording was silent or empty?')
        raise IgnorableError
    transcript = ""
    for result in data["results"]:
        transcript += result["alternatives"][0]["transcript"].strip() + " "
    return transcript


def custom_accept(self: QErrorMessage):
    QErrorMessage.accept(self)
    settings_dialog()


def show_error_dialog(message: str, show_settings_after: bool=False):
    error_dialog = QErrorMessage(mw)
    error_dialog.setWindowTitle(WINDOW_NAME)
    if show_settings_after:
        error_dialog.accept = lambda: custom_accept(error_dialog)
    error_dialog.showMessage(message)


def show_donate_dialog():
    donate_dialog = QMessageBox(mw)
    donate_dialog.setWindowTitle(WINDOW_NAME)
    donate_dialog.setText("We're extremely grateful for your support! "
                          "Donate here: <a href=\"https://www.paypal.com/donate/?hosted_button_id=5SMQLVSC5XA5W\">https://www.paypal.com/donate/?hosted_button_id=5SMQLVSC5XA5W</a>")
    donate_dialog.show()


def inline_diff(a, b, is_chinese: bool=False):
    # If we receive an array, this will diff words as opposed to letters, which makes more sense
    # for languages with spaces (like English). So the join_char is used to re-insert the spaces
    # back between the words and return a str, not a list.
    join_char = ' ' if isinstance(a, list) else ''
    matcher = difflib.SequenceMatcher(None, a, b)

    def process_tag(tag, i1, i2, j1, j2):
        if tag == 'equal':
            return join_char.join(to_pinyin(matcher.a[i1:i2]) if is_chinese else matcher.a[i1:i2])
        elif tag == 'replace':
            color = "red"
            seq = matcher.b[j1:j2]
        elif tag == 'delete':
            color = "orange"
            seq = matcher.a[i1:i2]
        elif tag == 'insert':
            color = "red"
            seq = matcher.b[j1:j2]
        else:
            assert False, f"Unknown tag {tag}"
        return f"<span style=\"color:{color}\">{join_char.join(to_pinyin(seq) if is_chinese else seq)}</span>"

    return join_char.join(process_tag(*t) for t in matcher.get_opcodes())


def to_pinyin(sent):
    return hanzi.to_pinyin(sent, accented=False)


def remove_html(s):
    return re.sub(REMOVE_HTML_RE, '', s)


def rstrip_punc(s):
    """ Strips all rightmost punctuation, based on Unicode characters. """
    ei = len(s)
    # The startswith('P') indicates punctuation
    while ei > 0 and category(s[ei - 1]).startswith('P'):
        ei -= 1
    return s[:ei]


# One disadvantage of doing it this way is that the output will look less correct (such as "dont" and "crosscountry").
# Alternately, I could only remove punctuation from beginning and end of words for space segmented languages.
# But that's more complex and also error prone if the input has hyphens but the STT output doesn't.
def strip_all_punc(s):
    return s.translate(PUNCTUATION_TABLE)


class SettingsDialog(QDialog):

    def __init__(self, my_settings: QSettings, *args, **kwargs):
        super(SettingsDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle(WINDOW_NAME + " Settings")
        self.my_settings = my_settings

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.api_key_textbox = QLineEdit()
        self.api_key_textbox.setText(self.my_settings.value(API_KEY_SETTING_NAME, "", type=str))
        api_setting_label = QLabel("Google Speech-to-Text API Key:")

        self.field_to_read_textbox = QLineEdit()
        self.field_to_read_textbox.setText(self.my_settings.value(FIELD_TO_READ_SETTING_NAME, FIELD_TO_READ_DEFAULT_NAME, type=str))
        field_to_read_setting_label = QLabel("Name of Card Field to Read:")

        self.select_language_dropdown = QComboBox()
        for ln in SUPPORTED_LANGUAGE_NAMES:
            self.select_language_dropdown.addItem(ln)
        self.select_language_dropdown.setCurrentText(self.my_settings.value(LANGUAGE_SETTING_NAME, '', type=str))
        select_language_label = QLabel("Language:")

        self.donateButton = QPushButton()
        self.donateButton.setText("Donate \u2764")
        self.donateButton.setFixedWidth(90)
        self.donateButton.clicked.connect(show_donate_dialog)

        api_hor = QHBoxLayout()
        api_hor.addWidget(api_setting_label)
        api_hor.addWidget(self.api_key_textbox)

        ftr_hor = QHBoxLayout()
        ftr_hor.addWidget(field_to_read_setting_label)
        ftr_hor.addWidget(self.field_to_read_textbox)

        sld_hor = QHBoxLayout()
        sld_hor.addWidget(select_language_label)
        sld_hor.addWidget(self.select_language_dropdown)

        self.layout = QVBoxLayout()
        self.layout.addLayout(sld_hor)
        self.layout.addLayout(ftr_hor)
        self.layout.addLayout(api_hor)
        self.layout.addWidget(self.donateButton)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def accept(self):
        self.my_settings.setValue(API_KEY_SETTING_NAME, self.api_key_textbox.text())
        self.my_settings.setValue(FIELD_TO_READ_SETTING_NAME, self.field_to_read_textbox.text())
        self.my_settings.setValue(LANGUAGE_SETTING_NAME, self.select_language_dropdown.currentText())
        super(SettingsDialog, self).accept()

    def reject(self):
        super(SettingsDialog, self).reject()


app_settings = QSettings(SETTINGS_ORGANIZATION, SETTINGS_APPLICATION)

cp_action = QAction("Test Your Pronunciation", mw)
cp_action.triggered.connect(test_pronunciation)
mw.form.menuTools.addAction(cp_action)
cp_action.setShortcut(QKeySequence("Ctrl+Shift+S"))

cps_action = QAction("Test Your Pronunciation Settings", mw)
cps_action.triggered.connect(settings_dialog)
mw.form.menuTools.addAction(cps_action)
