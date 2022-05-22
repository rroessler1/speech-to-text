from abc import ABC, abstractmethod
import base64
import requests
from ._vendor import speech_recognition as sr #import aifc #https://docs.python.org/3/library/aifc.html #https://peps.python.org/pep-0594/#aifc

# import the main window object (mw) from aqt
from aqt import mw
# import all of the Qt GUI library
from aqt.qt import *

from .exceptions import STTError


def get_stt_client(name, settings: QSettings):
#    if name == "apiai": #iOS
#        return apiaiClient(settings)
#    if name == "assemblyai":
#        return AssemblyAIClient(settings)
    if name == "google":
        return GoogleClient(settings)
    if name == "microsoft":
        return MicrosoftClient(settings)
    if name == "speechrecognition": # https://pypi.org/project/SpeechRecognition/
        return SRClient(settings)
#    if name == "ibm-watsom": #previously "watson-developer-cloud"
#        return WatsonClient(settings)
#    else https://realpython.com/python-speech-recognition/
    raise Exception("Invalid STT client name")


class STTClient(ABC):
    @abstractmethod
    def get_field_to_read(self):
        pass

    @abstractmethod
    def get_language_code(self):
        pass

    @abstractmethod
    def pre_stt_validate(self):
        """
            Does any required validation before recording audio.
            Specifically, it currently validates the API key is not empty.
            Throws an exception if validation fails.
        """
        pass

    @abstractmethod
    def get_stt_results(self, audio_file_path):
        """
            Call pre_stt_validate first, then call this.
        """
        pass

    @abstractmethod
    def get_my_settings_layout(self):
        pass

    @abstractmethod
    def save_settings(self):
        pass


class SRClient(STTClient):
    # Constants
    #API_KEY_SETTING_NAME1 = "sr-bing-key"
    ##API_KEY_SETTING_NAME2 = "sr-google-key"
    ##API_KEY_SETTING_NAME3 = "sr-google-cloud-key"
    #API_KEY_SETTING_NAME4 = "sr-houndify-client-id"
    #API_KEY_SETTING_NAME4b = "sr-houndify-client-key"
    #API_KEY_SETTING_NAME5 = "sr-ibm-username"
    #API_KEY_SETTING_NAME5b = "sr-ibm-password"
    #API_KEY_SETTING_NAME6 = "sr-sphinx-key"
    #API_KEY_SETTING_NAME7 = "sr-wit-key"
    API_KEY_SETTING_NAME = "sr-key"
    API_KEY_SETTING_NAME2 = "sr-key2"
    RECOGNIZER_SETTING_NAME = "sr-recognizer"
    RECOGNIZER_DEFAULT_NAME = "bing"
    RECOGNIZERS = ["bing", "google", "google_cloud", "houndify", "ibm", "sphinx", "wit"]
    RECOGNIZER_NAMES = ["Microsoft Bing Speech", "Google Web Speech API", "Google Cloud Speech", "Houndify", "IBM Speech to Text", "CMU Sphinx", "Wit.ai"]
    FIELD_TO_READ_SETTING_NAME = "field-to-read"
    FIELD_TO_READ_DEFAULT_NAME = "Front"
    LANGUAGE_SETTING_NAME = "language-name"

    def __init__(self, settings: QSettings):
        self.my_settings = settings
        self.r = sr.Recognizer()

        # Settings that we need to read later
        self.api_key_textbox = QLineEdit()
        self.api_key_textbox2 = QLineEdit()
        self.field_to_read_textbox = QLineEdit()
        self.select_recognizer_dropdown = QComboBox()
        self.select_language_dropdown = QComboBox()

    def get_field_to_read(self):
        return self.my_settings.value(SRClient.FIELD_TO_READ_SETTING_NAME, SRClient.FIELD_TO_READ_DEFAULT_NAME, type=str)

    def get_language_code(self):
        return next(
            iter([tag.partition("stt::language::")[2] for tag in mw.reviewer.card._note.tags if "stt::language::" in tag]),
            GoogleClient.SUPPORTED_LANGUAGE_CODES[GoogleClient.SUPPORTED_LANGUAGE_NAMES.index(
                self.my_settings.value(SRClient.LANGUAGE_SETTING_NAME, 'English (United States)', type=str))]
        )

    def pre_stt_validate(self):
        #alert("pre_stt_validate") #FIXME
        """
            Does any required validation before recording audio.
            Specifically, it currently validates the API key is not empty.
            Throws an exception if validation fails.
        """
        pass

    def get_stt_results(self, audio_file_path):
        #alert("get_stt_results") #FIXME
        """
            Call pre_stt_validate first, then call this.
        """
        
        # "Microsoft Bing Speech" → "bing" → r.recognize_bing()
        name = SRClient.RECOGNIZERS[SRClient.RECOGNIZER_NAMES.index(
            self.my_settings.value(SRClient.RECOGNIZER_SETTING_NAME, "Microsoft Bing Speech", type=str))]
        recdotwav = sr.AudioFile(audio_file_path)
        with recdotwav as source:
            audio = self.r.record(source)
        #getattr(self.r,"recognize_"+name)(audio)
        #recognize_name(audio)
        #recognize_name(audio, key)
        #recognize_name(audio, username, password)
        #recognize_name(audio, client_id, client_key)
        if name in ["google", "google-cloud", "sphinx"]:
            getattr(self.r,"recognize_"+name)(audio, language=self.get_language_code())
        elif name in ["bing", "wit"]:
            getattr(self.r,"recognize_"+name)(audio, 
                self.my_settings.value(SRClient.API_KEY_SETTING_NAME, "", type=str), 
                language=self.get_language_code())
        elif name in ["houndify", "ibm"]:
            getattr(self.r,"recognize_"+name)(audio, 
                self.my_settings.value(SRClient.API_KEY_SETTING_NAME, "", type=str), 
                self.my_settings.value(SRClient.API_KEY_SETTING_NAME2, "", type=str), 
                language=self.get_language_code())

    def get_my_settings_layout(self):
        my_settings_layout = QHBoxLayout()

        self.api_key_textbox.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME, "", type=str))
        self.api_key_textbox2.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME2, "", type=str))
        api_setting_label = QLabel("Key/Client ID/Username:")
        api_setting_label2 = QLabel("Client Key/Password:")

        self.field_to_read_textbox.setText(self.my_settings.value(SRClient.FIELD_TO_READ_SETTING_NAME, SRClient.FIELD_TO_READ_DEFAULT_NAME, type=str))
        field_to_read_setting_label = QLabel("Name of Card Field to Read:")

        for ln in SRClient.RECOGNIZER_NAMES:
            self.select_recognizer_dropdown.addItem(ln)
        self.select_recognizer_dropdown.setCurrentText(self.my_settings.value(SRClient.RECOGNIZER_SETTING_NAME, '', type=str))
        select_recognizer_label = QLabel("Recognizer:")

        for ln in GoogleClient.SUPPORTED_LANGUAGE_NAMES:
            self.select_language_dropdown.addItem(ln)
        self.select_language_dropdown.setCurrentText(self.my_settings.value(SRClient.LANGUAGE_SETTING_NAME, '', type=str))
        select_language_label = QLabel("Language:")

        labels_vl = QVBoxLayout()
        labels_vl.addWidget(select_recognizer_label)
        labels_vl.addWidget(select_language_label)
        labels_vl.addWidget(field_to_read_setting_label)
        labels_vl.addWidget(api_setting_label)
        labels_vl.addWidget(api_setting_label2)

        boxes_vl = QVBoxLayout()
        boxes_vl.addWidget(self.select_recognizer_dropdown)
        boxes_vl.addWidget(self.select_language_dropdown)
        boxes_vl.addWidget(self.field_to_read_textbox)
        boxes_vl.addWidget(self.api_key_textbox)
        boxes_vl.addWidget(self.api_key_textbox2)

        my_settings_layout.addLayout(labels_vl)
        my_settings_layout.addLayout(boxes_vl)

        return my_settings_layout

    def save_settings(self):
        self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME, self.api_key_textbox.text())
        self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME2, self.api_key_textbox2.text())
        self.my_settings.setValue(SRClient.FIELD_TO_READ_SETTING_NAME, self.field_to_read_textbox.text())
        self.my_settings.setValue(SRClient.RECOGNIZER_SETTING_NAME, self.select_recognizer_dropdown.currentText())
        self.my_settings.setValue(SRClient.LANGUAGE_SETTING_NAME, self.select_language_dropdown.currentText())


class GoogleClient(STTClient):
    # Constants
    API_KEY_SETTING_NAME = "google-stt-api-key"
    FIELD_TO_READ_SETTING_NAME = "field-to-read"
    FIELD_TO_READ_DEFAULT_NAME = "Front"
    LANGUAGE_SETTING_NAME = "language-name"
    SUPPORTED_LANGUAGE_CODES = ['af-ZA', 'sq-AL', 'am-ET', 'ar-DZ', 'ar-BH', 'ar-EG', 'ar-IQ', 'ar-IL', 'ar-JO', 'ar-KW', 'ar-LB', 'ar-MA', 'ar-OM', 'ar-QA', 'ar-SA', 'ar-PS', 'ar-TN', 'ar-AE', 'ar-YE', 'hy-AM', 'az-AZ', 'eu-ES', 'bn-BD', 'bn-IN', 'bs-BA', 'bg-BG', 'my-MM', 'ca-ES', 'yue-Hant-HK', 'zh', 'zh-TW', 'hr-HR', 'cs-CZ', 'da-DK', 'nl-BE', 'nl-NL', 'en-AU', 'en-CA', 'en-GH', 'en-HK', 'en-IN', 'en-IE', 'en-KE', 'en-NZ', 'en-NG', 'en-PK', 'en-PH', 'en-SG', 'en-ZA', 'en-TZ', 'en-GB', 'en-US', 'et-EE', 'fil-PH', 'fi-FI', 'fr-BE', 'fr-CA', 'fr-FR', 'fr-CH', 'gl-ES', 'ka-GE', 'de-AT', 'de-DE', 'de-CH', 'el-GR', 'gu-IN', 'iw-IL', 'hi-IN', 'hu-HU', 'is-IS', 'id-ID', 'it-IT', 'it-CH', 'ja-JP', 'jv-ID', 'kn-IN', 'km-KH', 'ko-KR', 'lo-LA', 'lv-LV', 'lt-LT', 'mk-MK', 'ms-MY', 'ml-IN', 'mr-IN', 'mn-MN', 'ne-NP', 'no-NO', 'fa-IR', 'pl-PL', 'pt-BR', 'pt-PT', 'pa-Guru-IN', 'ro-RO', 'ru-RU', 'sr-RS', 'si-LK', 'sk-SK', 'sl-SI', 'es-AR', 'es-BO', 'es-CL', 'es-CO', 'es-CR', 'es-DO', 'es-EC', 'es-SV', 'es-GT', 'es-HN', 'es-MX', 'es-NI', 'es-PA', 'es-PY', 'es-PE', 'es-PR', 'es-ES', 'es-US', 'es-UY', 'es-VE', 'su-ID', 'sw-KE', 'sw-TZ', 'sv-SE', 'ta-IN', 'ta-MY', 'ta-SG', 'ta-LK', 'te-IN', 'th-TH', 'tr-TR', 'uk-UA', 'ur-IN', 'ur-PK', 'uz-UZ', 'vi-VN', 'zu-ZA']
    SUPPORTED_LANGUAGE_NAMES = ['Afrikaans (South Africa)', 'Albanian (Albania)', 'Amharic (Ethiopia)', 'Arabic (Algeria)', 'Arabic (Bahrain)', 'Arabic (Egypt)', 'Arabic (Iraq)', 'Arabic (Israel)', 'Arabic (Jordan)', 'Arabic (Kuwait)', 'Arabic (Lebanon)', 'Arabic (Morocco)', 'Arabic (Oman)', 'Arabic (Qatar)', 'Arabic (Saudi Arabia)', 'Arabic (State of Palestine)', 'Arabic (Tunisia)', 'Arabic (United Arab Emirates)', 'Arabic (Yemen)', 'Armenian (Armenia)', 'Azerbaijani (Azerbaijan)', 'Basque (Spain)', 'Bengali (Bangladesh)', 'Bengali (India)', 'Bosnian (Bosnia and Herzegovina)', 'Bulgarian (Bulgaria)', 'Burmese (Myanmar)', 'Catalan (Spain)', 'Chinese, Cantonese (Traditional Hong Kong)', 'Chinese, Mandarin (Simplified, China)', 'Chinese, Mandarin (Traditional, Taiwan)', 'Croatian (Croatia)', 'Czech (Czech Republic)', 'Danish (Denmark)', 'Dutch (Belgium)', 'Dutch (Netherlands)', 'English (Australia)', 'English (Canada)', 'English (Ghana)', 'English (Hong Kong)', 'English (India)', 'English (Ireland)', 'English (Kenya)', 'English (New Zealand)', 'English (Nigeria)', 'English (Pakistan)', 'English (Philippines)', 'English (Singapore)', 'English (South Africa)', 'English (Tanzania)', 'English (United Kingdom)', 'English (United States)', 'Estonian (Estonia)', 'Filipino (Philippines)', 'Finnish (Finland)', 'French (Belgium)', 'French (Canada)', 'French (France)', 'French (Switzerland)', 'Galician (Spain)', 'Georgian (Georgia)', 'German (Austria)', 'German (Germany)', 'German (Switzerland)', 'Greek (Greece)', 'Gujarati (India)', 'Hebrew (Israel)', 'Hindi (India)', 'Hungarian (Hungary)', 'Icelandic (Iceland)', 'Indonesian (Indonesia)', 'Italian (Italy)', 'Italian (Switzerland)', 'Japanese (Japan)', 'Javanese (Indonesia)', 'Kannada (India)', 'Khmer (Cambodia)', 'Korean (South Korea)', 'Lao (Laos)', 'Latvian (Latvia)', 'Lithuanian (Lithuania)', 'Macedonian (North Macedonia)', 'Malay (Malaysia)', 'Malayalam (India)', 'Marathi (India)', 'Mongolian (Mongolia)', 'Nepali (Nepal)', 'Norwegian Bokmål (Norway)', 'Persian (Iran)', 'Polish (Poland)', 'Portuguese (Brazil)', 'Portuguese (Portugal)', 'Punjabi (Gurmukhi India)', 'Romanian (Romania)', 'Russian (Russia)', 'Serbian (Serbia)', 'Sinhala (Sri Lanka)', 'Slovak (Slovakia)', 'Slovenian (Slovenia)', 'Spanish (Argentina)', 'Spanish (Bolivia)', 'Spanish (Chile)', 'Spanish (Colombia)', 'Spanish (Costa Rica)', 'Spanish (Dominican Republic)', 'Spanish (Ecuador)', 'Spanish (El Salvador)', 'Spanish (Guatemala)', 'Spanish (Honduras)', 'Spanish (Mexico)', 'Spanish (Nicaragua)', 'Spanish (Panama)', 'Spanish (Paraguay)', 'Spanish (Peru)', 'Spanish (Puerto Rico)', 'Spanish (Spain)', 'Spanish (United States)', 'Spanish (Uruguay)', 'Spanish (Venezuela)', 'Sundanese (Indonesia)', 'Swahili (Kenya)', 'Swahili (Tanzania)', 'Swedish (Sweden)', 'Tamil (India)', 'Tamil (Malaysia)', 'Tamil (Singapore)', 'Tamil (Sri Lanka)', 'Telugu (India)', 'Thai (Thailand)', 'Turkish (Turkey)', 'Ukrainian (Ukraine)', 'Urdu (India)', 'Urdu (Pakistan)', 'Uzbek (Uzbekistan)', 'Vietnamese (Vietnam)', 'Zulu (South Africa)']

    def __init__(self, settings: QSettings):
        self.my_settings = settings

        # Settings that we need to read later
        self.api_key_textbox = QLineEdit()
        self.field_to_read_textbox = QLineEdit()
        self.select_language_dropdown = QComboBox()

    def get_field_to_read(self):
        return self.my_settings.value(GoogleClient.FIELD_TO_READ_SETTING_NAME, GoogleClient.FIELD_TO_READ_DEFAULT_NAME, type=str)

    def get_language_code(self):
        return next(
            iter([tag.partition("stt::language::")[2] for tag in mw.reviewer.card._note.tags if "stt::language::" in tag]),
            GoogleClient.SUPPORTED_LANGUAGE_CODES[GoogleClient.SUPPORTED_LANGUAGE_NAMES.index(
                self.my_settings.value(GoogleClient.LANGUAGE_SETTING_NAME, 'English (United States)', type=str))]
        )

    def get_api_key(self):
        return self.my_settings.value(GoogleClient.API_KEY_SETTING_NAME, "", type=str)

    def pre_stt_validate(self):
        if self.get_api_key() == '':
            raise STTError("Please set your API key.", True)

    def get_stt_results(self, audio_file_path):
        with open(audio_file_path, 'rb') as audio_content:
            encoded_audio = base64.b64encode(audio_content.read())

        payload = {
            "config": {
                "encoding": "ENCODING_UNSPECIFIED",
                "sampleRateHertz": "44100",
                "languageCode": self.get_language_code()
            },
            "audio": {
                "content": encoded_audio.decode("utf8")
            }
        }

        try:
            r = requests.post("https://speech.googleapis.com/v1/speech:recognize?key={}".format(self.get_api_key()),
                              json=payload)
        except requests.exceptions.ConnectionError:
            raise STTError(f"ConnectionError, could not access the Google Speech-to-Text service.\n"
                                 f"Are you sure you have an internet connection?")

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            if r.status_code == 400:
                raise STTError('Received an "Unauthorized" response; your API key is probably invalid.', True)
            # otherwise re-throw the exception
            raise
        data = r.json()
        if "results" not in data:
            raise STTError(
                'No results from Google Speech-to-Text service; maybe your audio recording was silent or empty?')
        transcript = ""
        for result in data["results"]:
            transcript += result["alternatives"][0]["transcript"].strip() + " "
        return transcript

    def get_my_settings_layout(self):
        my_settings_layout = QHBoxLayout()

        self.api_key_textbox.setText(self.my_settings.value(GoogleClient.API_KEY_SETTING_NAME, "", type=str))
        api_setting_label = QLabel("Google Speech-to-Text API Key:")

        self.field_to_read_textbox.setText(self.my_settings.value(GoogleClient.FIELD_TO_READ_SETTING_NAME, GoogleClient.FIELD_TO_READ_DEFAULT_NAME, type=str))
        field_to_read_setting_label = QLabel("Name of Card Field to Read:")

        for ln in GoogleClient.SUPPORTED_LANGUAGE_NAMES:
            self.select_language_dropdown.addItem(ln)
        self.select_language_dropdown.setCurrentText(self.my_settings.value(GoogleClient.LANGUAGE_SETTING_NAME, '', type=str))
        select_language_label = QLabel("Language:")

        labels_vl = QVBoxLayout()
        labels_vl.addWidget(select_language_label)
        labels_vl.addWidget(field_to_read_setting_label)
        labels_vl.addWidget(api_setting_label)

        boxes_vl = QVBoxLayout()
        boxes_vl.addWidget(self.select_language_dropdown)
        boxes_vl.addWidget(self.field_to_read_textbox)
        boxes_vl.addWidget(self.api_key_textbox)

        my_settings_layout.addLayout(labels_vl)
        my_settings_layout.addLayout(boxes_vl)

        return my_settings_layout

    def save_settings(self):
        self.my_settings.setValue(GoogleClient.API_KEY_SETTING_NAME, self.api_key_textbox.text())
        self.my_settings.setValue(GoogleClient.FIELD_TO_READ_SETTING_NAME, self.field_to_read_textbox.text())
        self.my_settings.setValue(GoogleClient.LANGUAGE_SETTING_NAME, self.select_language_dropdown.currentText())


class MicrosoftClient(STTClient):
    # Constants
    API_KEY_SETTING_NAME = "microsoft-stt-api-key"
    FIELD_TO_READ_SETTING_NAME = "microsoft-field-to-read"
    FIELD_TO_READ_DEFAULT_NAME = "Front"
    LANGUAGE_SETTING_NAME = "microsoft-language-name"
    REGION_SETTING_NAME = "microsoft-region"
    REGIONS = ["centralus", "eastus", "eastus2", "northcentralus", "southcentralus", "westcentralus", "westus", "westus2", "canadacentral", "brazilsouth", "eastasia", "southeastasia", "australiaeast", "centralindia", "japaneast", "japanwest", "koreacentral", "northeurope", "westeurope", "francecentral", "uksouth"]
    SUPPORTED_LANGUAGE_CODES = ["ar-BH", "ar-EG", "ar-IQ", "ar-IL", "ar-JO", "ar-KW", "ar-LB", "ar-OM", "ar-QA", "ar-SA", "ar-PS", "ar-SY", "ar-AE", "bg-BG", "ca-ES", "zh-HK", "zh-CN", "zh-TW", "hr-HR", "cs-CZ", "da-DK", "nl-NL", "en-AU", "en-CA", "en-GH", "en-HK", "en-IN", "en-IE", "en-KE", "en-NZ", "en-NG", "en-PH", "en-SG", "en-ZA", "en-TZ", "en-GB", "en-US", "et-EE", "fil-PH", "fi-FI", "fr-CA", "fr-FR", "fr-CH", "de-AT", "de-DE", "el-GR", "gu-IN", "hi-IN", "hu-HU", "id-ID", "ga-IE", "it-IT", "ja-JP", "ko-KR", "lv-LV", "lt-LT", "ms-MY", "mt-MT", "mr-IN", "nb-NO", "pl-PL", "pt-BR", "pt-PT", "ro-RO", "ru-RU", "sk-SK", "sl-SI", "es-AR", "es-BO", "es-CL", "es-CO", "es-CR", "es-CU", "es-DO", "es-EC", "es-SV", "es-GQ", "es-GT", "es-HN", "es-MX", "es-NI", "es-PA", "es-PY", "es-PE", "es-PR", "es-ES", "es-UY", "es-US", "es-VE", "sv-SE", "ta-IN", "te-IN", "th-TH", "tr-TR", "vi-VN"]
    SUPPORTED_LANGUAGE_NAMES = ["Arabic (Bahrain), modern standard", "Arabic (Egypt)", "Arabic (Iraq)", "Arabic (Israel)", "Arabic (Jordan)", "Arabic (Kuwait)", "Arabic (Lebanon)", "Arabic (Oman)", "Arabic (Qatar)", "Arabic (Saudi Arabia)", "Arabic (State of Palestine)", "Arabic (Syria)", "Arabic (United Arab Emirates)", "Bulgarian (Bulgaria)", "Catalan (Spain)", "Chinese (Cantonese, Traditional)", "Chinese (Mandarin, Simplified)", "Chinese (Taiwanese Mandarin)", "Croatian (Croatia)", "Czech (Czech Republic)", "Danish (Denmark)", "Dutch (Netherlands)", "English (Australia)", "English (Canada)", "English (Ghana)", "English (Hong Kong)", "English (India)", "English (Ireland)", "English (Kenya)", "English (New Zealand)", "English (Nigeria)", "English (Philippines)", "English (Singapore)", "English (South Africa)", "English (Tanzania)", "English (United Kingdom)", "English (United States)", "Estonian(Estonia)", "Filipino (Philippines)", "Finnish (Finland)", "French (Canada)", "French (France)", "French (Switzerland)", "German (Austria)", "German (Germany)", "Greek (Greece)", "Gujarati (Indian)", "Hindi (India)", "Hungarian (Hungary)", "Indonesian (Indonesia)", "Irish(Ireland)", "Italian (Italy)", "Japanese (Japan)", "Korean (Korea)", "Latvian (Latvia)", "Lithuanian (Lithuania)", "Malay (Malaysia)", "Maltese (Malta)", "Marathi (India)", "Norwegian (Bokmål, Norway)", "Polish (Poland)", "Portuguese (Brazil)", "Portuguese (Portugal)", "Romanian (Romania)", "Russian (Russia)", "Slovak (Slovakia)", "Slovenian (Slovenia)", "Spanish (Argentina)", "Spanish (Bolivia)", "Spanish (Chile)", "Spanish (Colombia)", "Spanish (Costa Rica)", "Spanish (Cuba)", "Spanish (Dominican Republic)", "Spanish (Ecuador)", "Spanish (El Salvador)", "Spanish (Equatorial Guinea)", "Spanish (Guatemala)", "Spanish (Honduras)", "Spanish (Mexico)", "Spanish (Nicaragua)", "Spanish (Panama)", "Spanish (Paraguay)", "Spanish (Peru)", "Spanish (Puerto Rico)", "Spanish (Spain)", "Spanish (Uruguay)", "Spanish (USA)", "Spanish (Venezuela)", "Swedish (Sweden)", "Tamil (India)", "Telugu (India)", "Thai (Thailand)", "Turkish (Turkey)", "Vietnamese (Vietnam)"]

    def __init__(self, settings: QSettings):
        self.my_settings = settings

        # Settings that we need to read later
        self.api_key_textbox = QLineEdit()
        self.field_to_read_textbox = QLineEdit()
        self.select_language_dropdown = QComboBox()
        self.select_region_dropdown = QComboBox()

    def get_field_to_read(self):
        return self.my_settings.value(MicrosoftClient.FIELD_TO_READ_SETTING_NAME, MicrosoftClient.FIELD_TO_READ_DEFAULT_NAME, type=str)

    def get_language_code(self):
        return next(
            iter([tag.partition("stt::language::")[2] for tag in mw.reviewer.card._note.tags if "stt::language::" in tag]),
            MicrosoftClient.SUPPORTED_LANGUAGE_CODES[MicrosoftClient.SUPPORTED_LANGUAGE_NAMES.index(
                self.my_settings.value(MicrosoftClient.LANGUAGE_SETTING_NAME, 'English (United States)', type=str))]
        )

    def get_api_key(self):
        return self.my_settings.value(MicrosoftClient.API_KEY_SETTING_NAME, "", type=str)

    def pre_stt_validate(self):
        if self.get_api_key() == '':
            raise STTError("Please set your API key.", True)

    def get_stt_results(self, audio_file_path):
        region = self.my_settings.value(MicrosoftClient.REGION_SETTING_NAME, "", type=str)
        url = "https://{}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1".format(region)
        query_params = {
            "language": self.get_language_code()
        }
        headers = {
            'Ocp-Apim-Subscription-Key': self.get_api_key(),
            "Content-type": "audio/wav; codecs=audio/pcm; samplerate=16000"
        }
        audio = open(audio_file_path, 'rb')

        try:
            r = requests.post(url, params=query_params, headers=headers, data=audio)
        except requests.exceptions.ConnectionError:
            raise STTError(f"ConnectionError, could not access the Microsoft Speech-to-Text service.\n"
                                 f"Are you sure you have an internet connection?")

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            if r.status_code == 401:
                raise STTError('Received an "Unauthorized" response; your API key is probably invalid, or you may have selected the wrong region.', True)
            # otherwise re-throw the exception
            raise

        json = r.json()
        if json["RecognitionStatus"] != "Success":
            raise STTError("Something was wrong with the audio, perhaps it was silent or just noise. "
                                 "Please try again.")
        return r.json()["DisplayText"]

    def save_settings(self):
        self.my_settings.setValue(MicrosoftClient.API_KEY_SETTING_NAME, self.api_key_textbox.text())
        self.my_settings.setValue(MicrosoftClient.FIELD_TO_READ_SETTING_NAME, self.field_to_read_textbox.text())
        self.my_settings.setValue(MicrosoftClient.LANGUAGE_SETTING_NAME, self.select_language_dropdown.currentText())
        self.my_settings.setValue(MicrosoftClient.REGION_SETTING_NAME, self.select_region_dropdown.currentText())

    def get_my_settings_layout(self):
        my_settings_layout = QHBoxLayout()

        self.api_key_textbox.setText(self.my_settings.value(MicrosoftClient.API_KEY_SETTING_NAME, "", type=str))
        api_setting_label = QLabel("Microsoft Speech-to-Text API Key:")

        self.field_to_read_textbox.setText(self.my_settings.value(MicrosoftClient.FIELD_TO_READ_SETTING_NAME, MicrosoftClient.FIELD_TO_READ_DEFAULT_NAME, type=str))
        field_to_read_setting_label = QLabel("Name of Card Field to Read:")

        for ln in MicrosoftClient.SUPPORTED_LANGUAGE_NAMES:
            self.select_language_dropdown.addItem(ln)
        self.select_language_dropdown.setCurrentText(
            self.my_settings.value(MicrosoftClient.LANGUAGE_SETTING_NAME, '', type=str))
        select_language_label = QLabel("Language:")

        for ln in MicrosoftClient.REGIONS:
            self.select_region_dropdown.addItem(ln)
        self.select_region_dropdown.setCurrentText(
            self.my_settings.value(MicrosoftClient.REGION_SETTING_NAME, '', type=str))
        select_region_label = QLabel("API Location:")

        labels_vl = QVBoxLayout()
        labels_vl.addWidget(select_language_label)
        labels_vl.addWidget(field_to_read_setting_label)
        labels_vl.addWidget(api_setting_label)
        labels_vl.addWidget(select_region_label)

        boxes_vl = QVBoxLayout()
        boxes_vl.addWidget(self.select_language_dropdown)
        boxes_vl.addWidget(self.field_to_read_textbox)
        boxes_vl.addWidget(self.api_key_textbox)
        boxes_vl.addWidget(self.select_region_dropdown)

        my_settings_layout.addLayout(labels_vl)
        my_settings_layout.addLayout(boxes_vl)

        return my_settings_layout
