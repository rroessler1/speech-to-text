from google.cloud import speech_v1 as speech
import dragonmapper
from dragonmapper import hanzi
import io



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


audio_path = "/home/ross/.local/share/Anki2/ross/collection.media/tmpshj9gn_1377171239634.mp3"
print(to_pinyin("他 要求 我 3點 之前 到 公司"))
# speech_to_text(audio_path)
