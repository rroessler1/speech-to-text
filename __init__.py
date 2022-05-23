import difflib
import re
from unicodedata import category

# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *
from aqt.sound import record_audio

addon_dir = os.path.dirname(os.path.realpath(__file__))
vendor_dir = os.path.join(addon_dir, "_vendor")
sys.path.append(vendor_dir)

from ._vendor.dragonmapper import hanzi
from .exceptions import STTError
from . import sttclients

# Constants:
WINDOW_NAME = "Test Your Pronunciation"
SETTINGS_ORGANIZATION = "github_rroessler1"
SETTINGS_APPLICATION = "stt-anki-plugin"
STT_CLIENT_SETTING_NAME = "stt-client"
STT_CLIENT_DEFAULT_NAME = "google"
CHINESE_LANGUAGE_CODES = {'zh-TW', 'zh', 'yue-Hant-HK', 'cmn-Hans-CN', 'cmn-Hant-TW', 'zh-HK', 'zh-CN'}
LANGUAGES_WITHOUT_SPACES = {
    # Chinese
    'zh-TW', 'zh', 'yue-Hant-HK', 'cmn-Hans-CN', 'cmn-Hant-TW', 'zh-HK', 'zh-CN',
    # Japanese
    'ja-JP',
    # Lao, Thai, Burmese, Khmer
    'lo-LA', 'th-TH', 'my-MM', 'km-KH'
}

PUNCTUATION_TABLE = dict.fromkeys(i for i in range(sys.maxunicode) if category(chr(i)).startswith('P'))
REMOVE_HTML_RE = re.compile('<[^<]+?>')


def settings_dialog():
    SettingsDialog(app_settings, stt_provider, mw).show()


def test_pronunciation():
    stt_client = stt_provider.stt_client

    # If they're not in study mode, use this as a shortcut to open settings
    if not mw.reviewer.card:
        settings_dialog()
        return

    # Make sure that the field on the card exists
    #field_to_read = stt_client.get_field_to_read()
    field_to_read = next(
        iter([tag.partition("stt::field::")[2] for tag in mw.reviewer.card._note.tags if "stt::field::" in tag]),
        stt_client.get_field_to_read()
    )
    if field_to_read not in mw.reviewer.card.note():
        show_error_dialog(f'This plugin needs to know which field you are reading. '
                                 f'It\'s looking for a field named: "{field_to_read}", '
                                 f'but there is no field named: "{field_to_read}" on the current card. '
                                 f'Please check the settings.',
                          True)
        return

    # Validate anything else
    try:
        stt_client.pre_stt_validate()
    except STTError as e:
        show_error_dialog(str(e), e.show_settings)
        return

    to_read_text = mw.reviewer.card.note()[field_to_read]
    to_read_text = strip_all_punc(remove_html(to_read_text)).strip()

    def after_record(recorded_voice):
        # If the user canceled the recording, do nothing and return
        if not recorded_voice:
            return
        try:
            tts_result = stt_client.get_stt_results(recorded_voice)
            tts_result = strip_all_punc(tts_result).strip()
            diff_and_show_result(to_read_text, tts_result, stt_client.get_language_code())
        except STTError as e:
            show_error_dialog(str(e), e.show_settings)
            return

    # This stores the file as "rec.wav" in a tmp directory (for me it's /tmp/anki_tmp/rec.wav)
    # It will overwrite the file every time, so there's no need to delete it after.
    record_audio(mw, mw, False, after_record)


def diff_and_show_result(to_read_text, tts_result, language_code):
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


def inline_diff(a, b, is_chinese: bool = False):
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
    no_html = re.sub(REMOVE_HTML_RE, '', s)
    return no_html.replace("&nbsp;", "")


# One disadvantage of doing it this way is that the output will look less correct (such as "dont" and "crosscountry").
# Alternately, I could only remove punctuation from beginning and end of words for space segmented languages.
# But that's more complex and also error prone if the input has hyphens but the STT output doesn't.
def strip_all_punc(s):
    return s.translate(PUNCTUATION_TABLE)


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


class STTProvider:

    def __init__(self, settings: QSettings):
        self.settings = settings
        self.update_from_settings()

    def update_from_settings(self):
        self.stt_client_name = self.settings.value(STT_CLIENT_SETTING_NAME, STT_CLIENT_DEFAULT_NAME, type=str)
        self.stt_client = sttclients.get_stt_client(self.stt_client_name, self.settings)

    def get_stt_client_name(self):
        return self.stt_client_name

    def get_stt_client(self):
        return self.stt_client


class SettingsDialog(QDialog):
    _FONT_HEADER = QFont()
    _FONT_HEADER.setPointSize(12)
    _FONT_HEADER.setBold(True)

    def __init__(self, my_settings: QSettings, my_stt_provider: STTProvider, *args, **kwargs):
        super(SettingsDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle(WINDOW_NAME + " Settings")
        self.my_settings = my_settings
        self.my_stt_provider = my_stt_provider

        self.base_layout = QVBoxLayout()
        self.service_combo_box = QComboBox()
        self.service_names = ["AssemblyAI", "Google Cloud", "Microsoft Azure", "SpeechRecognition"]
        self.service_combo_box.addItems(self.service_names)
        self.service_list = ["assemblyai", "google", "microsoft", "speechrecognition"]
        self.services = []
        self.service_combo_box.activated.connect(self.toggle_service)

        self.service_stack_layout = QStackedLayout()
        for idx, service_name in enumerate(self.service_list):
            service_label = QLabel(self.service_names[idx] + " Settings:")
            service_label.setFont(self._FONT_HEADER)

            layout = QVBoxLayout()
            layout.addWidget(service_label)

            service = sttclients.get_stt_client(service_name, my_settings)
            self.services.append(service)
            layout.addLayout(service.get_my_settings_layout())
            layout.setAlignment(Qt.AlignTop)

            widget = QWidget()
            widget.setLayout(layout)
            self.service_stack_layout.addWidget(widget)

        self.service_combo_box.setCurrentIndex(self.service_list.index(my_stt_provider.stt_client_name))
        self.toggle_service()

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.donateButton = QPushButton()
        self.donateButton.setText("Donate \u2764")
        self.donateButton.setFixedWidth(90)
        self.donateButton.clicked.connect(show_donate_dialog)

        select_service_label = QLabel("Select Text-to-Speech Service:")
        select_service_label.setFont(self._FONT_HEADER)

        hr = QFrame()
        hr.setFrameStyle(QFrame.HLine | QFrame.Sunken)
        hr.setLayout(QVBoxLayout())
        hr2 = QFrame()
        hr2.setFrameStyle(QFrame.HLine | QFrame.Sunken)
        hr2.setLayout(QVBoxLayout())

        self.base_layout.addWidget(select_service_label)
        self.base_layout.addWidget(self.service_combo_box)
        self.base_layout.addWidget(hr)
        self.base_layout.addLayout(self.service_stack_layout)
        self.base_layout.addWidget(hr2)
        self.base_layout.addWidget(self.donateButton)
        self.base_layout.addWidget(self.buttonBox)
        self.setLayout(self.base_layout)

    def toggle_service(self):
        self.service_stack_layout.setCurrentIndex(self.service_combo_box.currentIndex())

    def accept(self):
        self.services[self.service_combo_box.currentIndex()].save_settings()
        current_service_name = self.service_list[self.service_combo_box.currentIndex()]
        self.my_settings.setValue(STT_CLIENT_SETTING_NAME, current_service_name)
        super(SettingsDialog, self).accept()
        self.my_stt_provider.update_from_settings()

    def reject(self):
        super(SettingsDialog, self).reject()


app_settings = QSettings(SETTINGS_ORGANIZATION, SETTINGS_APPLICATION)
stt_provider = STTProvider(app_settings)

cp_action = QAction("Test Your Pronunciation", mw)
cp_action.triggered.connect(test_pronunciation)
mw.form.menuTools.addAction(cp_action)
cp_action.setShortcut(QKeySequence("Ctrl+Shift+S"))

cps_action = QAction("Test Your Pronunciation Settings", mw)
cps_action.triggered.connect(settings_dialog)
mw.form.menuTools.addAction(cps_action)
