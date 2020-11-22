import speech_recognition as sr
import pinyintools
from diff import inline_diff
import aifc

# obtain audio from the microphone
r = sr.Recognizer()
sents = ["今天好像會下雨，不過他想去夜市。",
"客廳在樓上還是樓下？",
"我昨天晚上在廚房做晚餐。",
"廁所在你的左邊。",
"超市右邊是我住在的大樓。",
"在日本，廁所跟浴室在不一樣的房間。"]

to_say = "我學了兩個鐘頭"
with sr.Microphone() as source:
    print("Say this sentence:")
    # audio = r.listen(source)

# recognize speech using Sphinx
# try:
#     print("Sphinx thinks you said " + r.recognize_sphinx(audio, language="zh-CN"))
# except sr.UnknownValueError:
#     print("Sphinx could not understand audio")
# except sr.RequestError as e:
#     print("Sphinx error; {0}".format(e))

# recognize speech using Google Cloud Speech
with open("GOOGLE_API_CREDENTIALS.json", 'r') as gcf:
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = gcf.read()

try:
    # hanzi = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS, language="zh-TW")
    hanzi = "我水了兩個鐘頭"
    to_say_pinyin = pinyintools.to_pinyin(to_say)
    pinyin = pinyintools.to_pinyin(hanzi)
    if to_say_pinyin != pinyin:
        print("You were supposed to say: {}".format(to_say))
        print(to_say_pinyin)
        print("Google heard you say:     {}".format(hanzi))
        print(pinyin)
        print("\n")
        print(inline_diff(to_say_pinyin, pinyin))
    else:
        print("Perfect. Google heard you say:")
        print(hanzi)
except sr.UnknownValueError:
    print("Google Cloud Speech could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Cloud Speech service; {0}".format(e))
