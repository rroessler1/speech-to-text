from abc import ABC, abstractmethod
import base64
import requests
from ._vendor import speech_recognition as sr #import aifc #https://docs.python.org/3/library/aifc.html #https://peps.python.org/pep-0594/#aifc
from ._vendor import assemblyai

# import the main window object (mw) from aqt
from aqt import mw
# import all of the Qt GUI library
from aqt.qt import *

from .exceptions import STTError


def get_stt_client(name, settings: QSettings):
#    if name == "apiai": #iOS
#        return apiaiClient(settings)
    if name == "assemblyai":
        return AssemblyAIClient(settings)
    if name == "google":
        return GoogleClient(settings)
    if name == "microsoft":
        return MicrosoftClient(settings)
    if name.startswith("sr-"): # https://pypi.org/project/SpeechRecognition/
        settings.setValue(SRClient.RECOGNIZER_SETTING_NAME, name.partition("sr-")[2]) #redundant line
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


class AssemblyAIClient(STTClient):
    # Constants
    API_KEY_SETTING_NAME = "assemblyai-key"
    FIELD_TO_READ_SETTING_NAME = "field-to-read"
    FIELD_TO_READ_DEFAULT_NAME = "Front"
    LANGUAGE_SETTING_NAME = "language-name"

    def __init__(self, settings: QSettings):
        self.my_settings = settings

        # Settings that we need to read later
        self.api_key_textbox = QLineEdit()
        self.field_to_read_textbox = QLineEdit()
        self.select_language_dropdown = QComboBox()

    def get_field_to_read(self):
        return self.my_settings.value(AssemblyAIClient.FIELD_TO_READ_SETTING_NAME, AssemblyAIClient.FIELD_TO_READ_DEFAULT_NAME, type=str)

    def get_language_code(self):
        return next(
            iter([tag.partition("stt::language::")[2] for tag in mw.reviewer.card._note.tags if "stt::language::" in tag]),
            GoogleClient.SUPPORTED_LANGUAGE_CODES[GoogleClient.SUPPORTED_LANGUAGE_NAMES.index(
                self.my_settings.value(AssemblyAIClient.LANGUAGE_SETTING_NAME, 'English (United States)', type=str))]
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
        aai = assemblyai.Client(token=AssemblyAIClient.API_KEY_SETTING_NAME)
        transcript = aai.transcribe(filename=audio_file_path)
        while transcript.status != 'completed':
            transcript = transcript.get()
        return transcript.text

    def get_my_settings_layout(self):
        my_settings_layout = QHBoxLayout()

        self.api_key_textbox.setText(self.my_settings.value(AssemblyAIClient.API_KEY_SETTING_NAME, "", type=str))
        api_setting_label = QLabel("AssemblyAI token:")

        self.field_to_read_textbox.setText(self.my_settings.value(AssemblyAIClient.FIELD_TO_READ_SETTING_NAME, AssemblyAIClient.FIELD_TO_READ_DEFAULT_NAME, type=str))
        field_to_read_setting_label = QLabel("Name of Card Field to Read:")

        for ln in GoogleClient.SUPPORTED_LANGUAGE_NAMES:
            self.select_language_dropdown.addItem(ln)
        self.select_language_dropdown.setCurrentText(self.my_settings.value(AssemblyAIClient.LANGUAGE_SETTING_NAME, '', type=str))
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
        self.my_settings.setValue(AssemblyAIClient.API_KEY_SETTING_NAME, self.api_key_textbox.text())
        self.my_settings.setValue(AssemblyAIClient.FIELD_TO_READ_SETTING_NAME, self.field_to_read_textbox.text())
        self.my_settings.setValue(AssemblyAIClient.LANGUAGE_SETTING_NAME, self.select_language_dropdown.currentText())


class SRClient(STTClient):
    # Constants
    API_KEY_SETTING_NAME01 = "sr_api_client_access_token" #name01
    API_KEY_SETTING_NAME02 = "sr_api_session_id"
    API_KEY_SETTING_NAME03 = "sr_bing_key"
    API_KEY_SETTING_NAME04 = "sr_google_key"
    API_KEY_SETTING_NAME05 = "sr_google_cloud_credentials_json"
    API_KEY_SETTING_NAME06 = "sr_houndify_client_id"
    API_KEY_SETTING_NAME07 = "sr_houndify_client_key"
    API_KEY_SETTING_NAME08 = "sr_ibm_username"
    API_KEY_SETTING_NAME09 = "sr_ibm_password"
    API_KEY_SETTING_NAME10 = "sr_wit_key"
    API_KEY_SETTING_NAME11 = "sr_azure_key"
    API_KEY_SETTING_NAME12 = "sr_azure_location"
    API_KEY_SETTING_NAME13 = "sr_amazon_lex_bot_name"
    API_KEY_SETTING_NAME14 = "sr_amazon_lex_bot_alias"
    API_KEY_SETTING_NAME15 = "sr_amazon_lex_user_id"
    API_KEY_SETTING_NAME16 = "sr_amazon_lex_access_key_id"
    API_KEY_SETTING_NAME17 = "sr_amazon_lex_secret_access_key"
    API_KEY_SETTING_NAME18 = "sr_amazon_bucket_name"
    API_KEY_SETTING_NAME19 = "sr_amazon_access_key_id"
    API_KEY_SETTING_NAME20 = "sr_amazon_secret_access_key"
    API_KEY_SETTING_NAME21 = "sr_amazon_region"
    API_KEY_SETTING_NAME22 = "sr_amazon_job_name"
    API_KEY_SETTING_NAME23 = "sr_amazon_file_key"
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
        self.api_key_textbox01 = QLineEdit() #name02
        self.api_key_textbox02 = QLineEdit()
        self.api_key_textbox03 = QLineEdit()
        self.api_key_textbox04 = QLineEdit()
        self.api_key_textbox05 = QLineEdit()
        self.api_key_textbox06 = QLineEdit()
        self.api_key_textbox07 = QLineEdit()
        self.api_key_textbox08 = QLineEdit()
        self.api_key_textbox09 = QLineEdit()
        self.api_key_textbox10 = QLineEdit()
        self.api_key_textbox11 = QLineEdit()
        self.api_key_textbox12 = QLineEdit()
        self.api_key_textbox13 = QLineEdit()
        self.api_key_textbox14 = QLineEdit()
        self.api_key_textbox15 = QLineEdit()
        self.api_key_textbox16 = QLineEdit()
        self.api_key_textbox17 = QLineEdit()
        self.api_key_textbox18 = QLineEdit()
        self.api_key_textbox19 = QLineEdit()
        self.api_key_textbox20 = QLineEdit()
        self.api_key_textbox21 = QLineEdit()
        self.api_key_textbox22 = QLineEdit()
        self.api_key_textbox23 = QLineEdit()
        self.field_to_read_textbox = QLineEdit()
#        self.select_recognizer_dropdown = QComboBox()
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
        """
            Does any required validation before recording audio.
            Specifically, it currently validates the API key is not empty.
            Throws an exception if validation fails.
        """
        case = name = next(
            iter([tag.partition("stt::service::sr-")[2] for tag in mw.reviewer.card._note.tags if "stt::service::sr-" in tag]),
            self.my_settings.value(SRClient.RECOGNIZER_SETTING_NAME, "Microsoft Bing Speech", type=str)
        )
        sr_api_client_access_token	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME01, "", type=str) #name03
        sr_api_session_id	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME02, "", type=str)
        sr_bing_key	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME03, "", type=str)
        sr_google_key	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME04, "", type=str)
        sr_google_cloud_credentials_json	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME05, "", type=str)
        sr_houndify_client_id	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME06, "", type=str)
        sr_houndify_client_key	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME07, "", type=str)
        sr_ibm_username	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME08, "", type=str)
        sr_ibm_password	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME09, "", type=str)
        sr_wit_key	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME10, "", type=str)
        sr_azure_key	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME11, "", type=str)
        sr_azure_location	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME12, "", type=str)
        sr_amazon_lex_bot_name	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME13, "", type=str)
        sr_amazon_lex_bot_alias	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME14, "", type=str)
        sr_amazon_lex_user_id	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME15, "", type=str)
        sr_amazon_lex_access_key_id	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME16, "", type=str)
        sr_amazon_lex_secret_access_key	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME17, "", type=str)
        sr_amazon_bucket_name	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME18, "", type=str)
        sr_amazon_access_key_id	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME19, "", type=str)
        sr_amazon_secret_access_key	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME20, "", type=str)
        sr_amazon_region	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME21, "", type=str)
        sr_amazon_job_name	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME22, "", type=str)
        sr_amazon_file_key	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME23, "", type=str)
        #switch name:
        if case=="api" and not(sr_api_client_access_token and sr_api_session_id):
            raise STTError("Please set sr_api_client_access_token and sr_api_session_id.", True)
        if case=="bing" and not(sr_bing_key):
            raise STTError("Please set sr_bing_key.", True)
        if case=="google" and not(sr_google_key):
            raise STTError("Please set sr_google_key.", True)
        if case=="google_cloud" and not(sr_google_cloud_credentials_json):
            raise STTError("Please set sr_google_cloud_credentials_json.", True)
        if case=="houndify" and not(sr_houndify_client_id and sr_houndify_client_key):
            raise STTError("Please set sr_houndify_client_id and sr_houndify_client_key.", True)
        if case=="ibm" and not(sr_ibm_username and sr_ibm_password):
            raise STTError("Please set sr_ibm_username and sr_ibm_password.", True)
        if case=="sphinx":
            pass
        if case=="wit" and not(sr_wit_key):
            raise STTError("Please set sr_wit_key.", True)
        if case=="azure"	and not(sr_azure_key):
            raise STTError("Please set sr_azure_key.", True)
        if case=="amazon-lex"	and not(sr_amazon_lex_bot_name and sr_amazon_lex_bot_alias and sr_amazon_lex_user_id and sr_amazon_lex_access_key_id and sr_amazon_lex_secret_access_key and sr_amazon_lex_region):
            raise STTError("Please set sr_amazon_lex_bot_name and sr_amazon_lex_bot_alias and sr_amazon_lex_user_id and sr_amazon_lex_access_key_id and sr_amazon_lex_secret_access_key and sr_amazon_lex_region.", True)
        if case=="amazon" and not(sr_amazon_bucket_name and sr_amazon_access_key_id and sr_amazon_secret_access_key and sr_amazon_region and sr_amazon_job_name and sr_amazon_file_key):
            raise STTError("Please set sr_amazon_bucket_name and sr_amazon_access_key_id and sr_amazon_secret_access_key and sr_amazon_region and sr_amazon_job_name and sr_amazon_file_key.", True)
        if case=="tensorflow":
            pass
        if case=="vosk":
            pass

    def get_stt_results(self, audio_file_path):
        """
            Call pre_stt_validate first, then call this.
        """
        
        case = name = next(
            iter([tag.partition("stt::service::sr-")[2] for tag in mw.reviewer.card._note.tags if "stt::service::sr-" in tag]),
            self.my_settings.value(SRClient.RECOGNIZER_SETTING_NAME, "Microsoft Bing Speech", type=str)
        )
        sr_api_client_access_token	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME01, "", type=str) #name03
        sr_api_session_id	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME02, "", type=str)
        sr_bing_key	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME03, "", type=str)
        sr_google_key	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME04, "", type=str)
        sr_google_cloud_credentials_json	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME05, "", type=str)
        sr_houndify_client_id	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME06, "", type=str)
        sr_houndify_client_key	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME07, "", type=str)
        sr_ibm_username	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME08, "", type=str)
        sr_ibm_password	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME09, "", type=str)
        sr_wit_key	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME10, "", type=str)
        sr_azure_key	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME11, "", type=str)
        sr_azure_location	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME12, "", type=str)
        sr_amazon_lex_bot_name	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME13, "", type=str)
        sr_amazon_lex_bot_alias	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME14, "", type=str)
        sr_amazon_lex_user_id	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME15, "", type=str)
        sr_amazon_lex_access_key_id	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME16, "", type=str)
        sr_amazon_lex_secret_access_key	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME17, "", type=str)
        sr_amazon_bucket_name	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME18, "", type=str)
        sr_amazon_access_key_id	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME19, "", type=str)
        sr_amazon_secret_access_key	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME20, "", type=str)
        sr_amazon_region	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME21, "", type=str)
        sr_amazon_job_name	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME22, "", type=str)
        sr_amazon_file_key	= self.my_settings.value(SRClient.API_KEY_SETTING_NAME23, "", type=str)
        l = self.get_language_code()
        recdotwav = sr.AudioFile(audio_file_path)
        with recdotwav as source:
            audio = self.r.record(source)
        #switch name:
        if case=="api":	return self.r.recognize_api(	audio, sr_api_client_access_token, language=l, session_id=sr_api_session_id) #show_all
        if case=="bing":	return self.r.recognize_bing(	audio, sr_bing_key, language=l) #show_all
        if case=="google":	return self.r.recognize_google(	audio, sr_google_key, language=l) #show_all
        if case=="google_cloud":	return self.r.recognize_google_cloud(	audio, credentials_json=sr_google_cloud_credentials_json, language=l) #preferred_phrases, show_all
        if case=="houndify":	return self.r.recognize_houndify(	audio, sr_houndify_client_id, sr_houndify_client_key) #show_all
        if case=="ibm":	return self.r.recognize_ibm(	audio, sr_ibm_username, sr_ibm_password, language=l) #show_all
        if case=="sphinx":	return self.r.recognize_sphinx(	audio, language=l) #keyword_entries, grammar, show_all
        if case=="wit":	return self.r.recognize_wit(	audio, sr_wit_key) #show_all
        if case=="azure":	return self.r.recognize_azure(	audio, sr_azure_key, language=l)#, profanity="masked", location="westus", show_all=False)
        if case=="amazon-lex":	return self.r.recognize_lex(	audio, bot_name=sr_amazon_lex_bot_name, bot_alias=sr_amazon_lex_bot_alias, user_id=sr_amazon_lex_user_id, content_type="audio/l16; rate=16000; channels=1", access_key_id=sr_amazon_lex_access_key_id, secret_access_key=sr_amazon_lex_secret_access_key, region=sr_amazon_lex_region)
        if case=="amazon":	return self.r.recognize_amazon(	audio, bucket_name=sr_amazon_bucket_name, access_key_id=sr_amazon_access_key_id, secret_access_key=sr_amazon_secret_access_key, region=sr_amazon_region, job_name=sr_amazon_job_name, file_key=sr_amazon_file_key)
        if case=="tensorflow":	return self.r.recognize_tensorflow(	audio)#, tensor_graph='tensorflow-data/conv_actions_frozen.pb', tensor_label='tensorflow-data/conv_actions_labels.txt')
        if case=="vosk":	return self.r.recognize_vosk(	audio, language=l)

    def get_my_settings_layout(self):
        my_settings_layout = QHBoxLayout()

        self.api_key_textbox01.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME01, "", type=str)) #name04
        self.api_key_textbox02.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME02, "", type=str))
        self.api_key_textbox03.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME03, "", type=str))
        self.api_key_textbox04.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME04, "", type=str))
        self.api_key_textbox05.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME05, "", type=str))
        self.api_key_textbox06.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME06, "", type=str))
        self.api_key_textbox07.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME07, "", type=str))
        self.api_key_textbox08.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME08, "", type=str))
        self.api_key_textbox09.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME09, "", type=str))
        self.api_key_textbox10.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME10, "", type=str))
        self.api_key_textbox11.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME11, "", type=str))
        self.api_key_textbox12.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME12, "", type=str))
        self.api_key_textbox13.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME13, "", type=str))
        self.api_key_textbox14.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME14, "", type=str))
        self.api_key_textbox15.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME15, "", type=str))
        self.api_key_textbox16.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME16, "", type=str))
        self.api_key_textbox17.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME17, "", type=str))
        self.api_key_textbox18.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME18, "", type=str))
        self.api_key_textbox19.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME19, "", type=str))
        self.api_key_textbox20.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME20, "", type=str))
        self.api_key_textbox21.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME21, "", type=str))
        self.api_key_textbox22.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME22, "", type=str))
        self.api_key_textbox23.setText(self.my_settings.value(SRClient.API_KEY_SETTING_NAME23, "", type=str))
        api_setting_label01 = QLabel("API client access token:") #name05
        api_setting_label02 = QLabel("API session id:")
        api_setting_label03 = QLabel("Bing key:")
        api_setting_label04 = QLabel("Google key:")
        api_setting_label05 = QLabel("Google cloud credentials json:")
        api_setting_label06 = QLabel("Houndify client id:")
        api_setting_label07 = QLabel("Houndify client key:")
        api_setting_label08 = QLabel("IBM username:")
        api_setting_label09 = QLabel("IBM password:")
        api_setting_label10 = QLabel("Wit key:")
        api_setting_label11 = QLabel("Azure key:")
        api_setting_label12 = QLabel("Azure location:")
        api_setting_label13 = QLabel("Amazon Lex bot_name:")
        api_setting_label14 = QLabel("Amazon Lex bot_alias:")
        api_setting_label15 = QLabel("Amazon Lex user_id:")
        api_setting_label16 = QLabel("Amazon Lex access_key_id:")
        api_setting_label17 = QLabel("Amazon Lex secret_access_key:")
        api_setting_label18 = QLabel("Amazon Transcribe bucket_name:")
        api_setting_label19 = QLabel("Amazon Transcribe access_key_id:")
        api_setting_label20 = QLabel("Amazon Transcribe secret_access_key:")
        api_setting_label21 = QLabel("Amazon Transcribe region:")
        api_setting_label22 = QLabel("Amazon Transcribe job_name:")
        api_setting_label23 = QLabel("Amazon Transcribe file_key:")

        self.field_to_read_textbox.setText(self.my_settings.value(SRClient.FIELD_TO_READ_SETTING_NAME, SRClient.FIELD_TO_READ_DEFAULT_NAME, type=str))
        field_to_read_setting_label = QLabel("Name of Card Field to Read:")

#        for ln in SRClient.RECOGNIZER_NAMES:
#            self.select_recognizer_dropdown.addItem(ln)
#        self.select_recognizer_dropdown.setCurrentText(self.my_settings.value(SRClient.RECOGNIZER_SETTING_NAME, '', type=str))
#        select_recognizer_label = QLabel("Recognizer:")

        for ln in GoogleClient.SUPPORTED_LANGUAGE_NAMES:
            self.select_language_dropdown.addItem(ln)
        self.select_language_dropdown.setCurrentText(self.my_settings.value(SRClient.LANGUAGE_SETTING_NAME, '', type=str))
        select_language_label = QLabel("Language:")

        labels_vl = QVBoxLayout()
#        labels_vl.addWidget(select_recognizer_label)
        labels_vl.addWidget(select_language_label)
        labels_vl.addWidget(field_to_read_setting_label)
        case = name = self.my_settings.value(SRClient.RECOGNIZER_SETTING_NAME, "Microsoft Bing Speech", type=str)
        if case=="api":
            labels_vl.addWidget(api_setting_label01) #name06
            labels_vl.addWidget(api_setting_label02)
        if case=="bing":
            labels_vl.addWidget(api_setting_label03)
        if case=="google":
            labels_vl.addWidget(api_setting_label04)
        if case=="google_cloud":
            labels_vl.addWidget(api_setting_label05)
        if case=="houndify":
            labels_vl.addWidget(api_setting_label06)
            labels_vl.addWidget(api_setting_label07)
        if case=="ibm":
            labels_vl.addWidget(api_setting_label08)
            labels_vl.addWidget(api_setting_label09)
        #if case=="sphinx":
        if case=="wit":
            labels_vl.addWidget(api_setting_label10)
        if case=="azure":
            labels_vl.addWidget(api_setting_label11)
            labels_vl.addWidget(api_setting_label12)
        if case=="amazon-lex":
            labels_vl.addWidget(api_setting_label13)
            labels_vl.addWidget(api_setting_label14)
            labels_vl.addWidget(api_setting_label15)
            labels_vl.addWidget(api_setting_label16)
            labels_vl.addWidget(api_setting_label17)
        if case=="amazon":
            labels_vl.addWidget(api_setting_label18)
            labels_vl.addWidget(api_setting_label19)
            labels_vl.addWidget(api_setting_label20)
            labels_vl.addWidget(api_setting_label21)
            labels_vl.addWidget(api_setting_label22)
            labels_vl.addWidget(api_setting_label23)
        #if case=="tensorflow":
        #if case=="vosk":

        boxes_vl = QVBoxLayout()
#        boxes_vl.addWidget(self.select_recognizer_dropdown)
        boxes_vl.addWidget(self.select_language_dropdown)
        boxes_vl.addWidget(self.field_to_read_textbox)
        if case=="api":
            boxes_vl.addWidget(self.api_key_textbox01) #name07
            boxes_vl.addWidget(self.api_key_textbox02)
        if case=="bing":
            boxes_vl.addWidget(self.api_key_textbox03)
        if case=="google":
            boxes_vl.addWidget(self.api_key_textbox04)
        if case=="google_cloud":
            boxes_vl.addWidget(self.api_key_textbox05)
        if case=="houndify":
            boxes_vl.addWidget(self.api_key_textbox06)
            boxes_vl.addWidget(self.api_key_textbox07)
        if case=="ibm":
            boxes_vl.addWidget(self.api_key_textbox08)
            boxes_vl.addWidget(self.api_key_textbox09)
        #if case=="sphinx":
        if case=="wit":
            boxes_vl.addWidget(self.api_key_textbox10)
        if case=="azure":
            boxes_vl.addWidget(self.api_key_textbox11)
            boxes_vl.addWidget(self.api_key_textbox12)
        if case=="amazon-lex":
            boxes_vl.addWidget(self.api_key_textbox13)
            boxes_vl.addWidget(self.api_key_textbox14)
            boxes_vl.addWidget(self.api_key_textbox15)
            boxes_vl.addWidget(self.api_key_textbox16)
            boxes_vl.addWidget(self.api_key_textbox17)
        if case=="amazon":
            boxes_vl.addWidget(self.api_key_textbox18)
            boxes_vl.addWidget(self.api_key_textbox19)
            boxes_vl.addWidget(self.api_key_textbox20)
            boxes_vl.addWidget(self.api_key_textbox21)
            boxes_vl.addWidget(self.api_key_textbox22)
            boxes_vl.addWidget(self.api_key_textbox23)
        #if case=="tensorflow":
        #if case=="vosk":

        my_settings_layout.addLayout(labels_vl)
        my_settings_layout.addLayout(boxes_vl)

        return my_settings_layout

    def save_settings(self):
        case = name = self.my_settings.value(SRClient.RECOGNIZER_SETTING_NAME, "Microsoft Bing Speech", type=str)
        #case = name = self.my_settings.value(STT_CLIENT_SETTING_NAME, "Microsoft Bing Speech", type=str)
        if case=="api":
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME01, self.api_key_textbox01.text()) #name08
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME02, self.api_key_textbox02.text())
        if case=="bing":
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME03, self.api_key_textbox03.text())
        if case=="google":
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME04, self.api_key_textbox04.text())
        if case=="google_cloud":
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME05, self.api_key_textbox05.text())
        if case=="houndify":
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME06, self.api_key_textbox06.text())
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME07, self.api_key_textbox07.text())
        if case=="ibm":
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME08, self.api_key_textbox08.text())
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME09, self.api_key_textbox09.text())
        #if case=="sphinx":
        if case=="wit":
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME10, self.api_key_textbox10.text())
        if case=="azure":
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME11, self.api_key_textbox11.text())
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME12, self.api_key_textbox12.text())
        if case=="amazon-lex":
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME13, self.api_key_textbox13.text())
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME14, self.api_key_textbox14.text())
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME15, self.api_key_textbox15.text())
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME16, self.api_key_textbox16.text())
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME17, self.api_key_textbox17.text())
        if case=="amazon":
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME18, self.api_key_textbox18.text())
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME19, self.api_key_textbox19.text())
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME20, self.api_key_textbox20.text())
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME21, self.api_key_textbox21.text())
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME22, self.api_key_textbox22.text())
            self.my_settings.setValue(SRClient.API_KEY_SETTING_NAME23, self.api_key_textbox23.text())
        #if case=="tensorflow":
        #if case=="vosk":
        self.my_settings.setValue(SRClient.FIELD_TO_READ_SETTING_NAME, self.field_to_read_textbox.text())
#        self.my_settings.setValue(SRClient.RECOGNIZER_SETTING_NAME, self.select_recognizer_dropdown.currentText())
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
