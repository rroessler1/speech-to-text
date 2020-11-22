import speech_recognition as sr

# obtain audio from the microphone
r = sr.Recognizer()
# recognize speech using Google Cloud Speech
with open("GOOGLE_API_CREDENTIALS.json", 'r') as gcf:
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = gcf.read()


def get_pronunciation():
    with sr.Microphone() as source:
        print("pre listen")
        audio = r.listen(source)
        print("post listen")
    try:
        print("pre recognize")
        return r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS, language="zh-TW")
    except sr.UnknownValueError:
        print("Google Cloud Speech could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Cloud Speech service; {0}".format(e))
