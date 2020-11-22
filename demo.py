from google.cloud import speech_v1 as speech
import dragonmapper
import io
import base64
import requests


def speech_to_text(local_speech_file):
    client = speech.SpeechClient()
    with io.open(local_speech_file, "rb") as audio_file:
        audio_content = audio_file.read()

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(dict(
        encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
        sample_rate_hertz=16000,
        language_code="zh-TW",
    ))

    response = client.recognize(config=config, audio=audio)
    print_sentences(response)


def to_pinyin(hanzi):
    return dragonmapper.hanzi.to_pinyin(hanzi, accented=False)


def print_sentences(response):
    for result in response.results:
        best_alternative = result.alternatives[0]
        transcript = best_alternative.transcript
        confidence = best_alternative.confidence
        print("-" * 80)
        print(f"Transcript: {transcript}")
        print(f"Confidence: {confidence:.0%}")


def rest_request(audio_file_path):

    with open(audio_file_path, 'rb') as audio_content:
        encoded_audio = base64.b64encode(audio_content.read())

    payload = {
        "config": {
            "encoding": "ENCODING_UNSPECIFIED",
            "sampleRateHertz": "16000",
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

    with open("API_KEY.txt", 'r') as api_key_file:
        API_KEY = api_key_file.read()
    r = requests.post("https://speech.googleapis.com/v1/speech:recognize?key={}".format(API_KEY), headers=headers, json=payload)
    r.raise_for_status()

    data = r.json()
    transcript = ""
    for result in data["results"]:
        transcript += result["alternatives"][0]["transcript"].strip() + " "
    print(transcript)


audio_path = "/home/ross/.local/share/Anki2/ross/collection.media/tmpshj9gn_1377171239634.mp3"
rest_request(audio_path)
# print(to_pinyin("他 要求 我 3點 之前 到 公司"))
# speech_to_text(audio_path)
