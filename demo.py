from google.cloud import speech_v1 as speech
import dragonmapper
import io
import base64
import json
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

    # with open(audio_file_path, 'rb') as audio_content:
    #     encoded_audio = base64.b64encode(audio_content.read())

    url = "https://eastasia.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
    query_params = {
        "language": "zh-CN"
    }

    # Pronunciation stuff
    # referenceText = "語言是交流的基礎"
    referenceText = "預約只有一天"
    pronAssessmentParamsJson = "{\"ReferenceText\":\"%s\",\"GradingSystem\":\"HundredMark\",\"Dimension\":\"Comprehensive\"}" % referenceText
    pronAssessmentParamsBase64 = base64.b64encode(bytes(pronAssessmentParamsJson, 'utf-8'))
    pronAssessmentParams = str(pronAssessmentParamsBase64, "utf-8")

    headers = {
        'Ocp-Apim-Subscription-Key': 'fill_in_key',
        "Content-type": "audio/wav; codecs=audio/pcm; samplerate=16000",
        # 'Pronunciation-Assessment': pronAssessmentParams,
    }

    audio = open(audio_file_path, 'rb') # encoded_audio.decode("utf8")

    r = requests.post(url, params=query_params, headers=headers, data=audio)
    r.raise_for_status()

    resultJson = json.loads(r.text)
    print(json.dumps(resultJson, indent=2, ensure_ascii=False))
    #
    data = r.json()
    print(data["DisplayText"])
    # transcript = ""
    # for result in data["results"]:
    #     transcript += result["alternatives"][0]["transcript"].strip() + " "
    # print(transcript)


# audio_path = "/home/ross/.local/share/Anki2/ross/collection.media/tmpshj9gn_1377171239634.mp3"
audio_path = "/home/ross/.local/share/Anki2/ross/collection.media/rec.wav"
rest_request(audio_path)
# print(to_pinyin("他 要求 我 3點 之前 到 公司"))
# speech_to_text(audio_path)
