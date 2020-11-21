import speech_recognition as sr

# obtain audio from the microphone
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    audio = r.listen(source)

# recognize speech using Sphinx
try:
    print("Sphinx thinks you said " + r.recognize_sphinx(audio, language="zh-CN"))
except sr.UnknownValueError:
    print("Sphinx could not understand audio")
except sr.RequestError as e:
    print("Sphinx error; {0}".format(e))

# recognize speech using Google Cloud Speech
GOOGLE_CLOUD_SPEECH_CREDENTIALS = r"""{
  "type": "service_account",
  "project_id": "speechtotext-296213",
  "private_key_id": "bb8ab5dbef0cff4bbe30543ef9e2e6fb6c488ac1",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCdPrWWS3JCZrAK\nTvDT0RkV1zia03Ub5BRQOdzAKFMmr6zlYMmwo2gsxazMXmLAqNfFdB1jMrpExQjv\nrT1DVkl1TwjM+315UqP2CpwayF8Bt3OlNqYEQ+CnjBRjyWQG3gJcxAVsGI7H6794\nVJP51aA12g6bPXfmaqmdzXcnNhyr1GLYpPPS5N3UYdCmi3Cokh8mVOSiCZPSU8+y\nXsmgeDLXHDG3OzDjRfjoFD0zDYUXWunasY1TOVUHFdm1rI9H3aAwf7l/bPiCKVGl\nHSQ0+AjI7M4Pk3R73yV5AxULtZHhTeLBFzTpZ4Ocw3rseSWAGWMlgKJTj9YXW+N1\nq4tOeUYXAgMBAAECggEAMNfaxd2Xl0KYagtNSS5JMXyRy53lYY1+NdFTXajo8zpc\nZT+kRqbrZATfAPhMinWn2GCSBE8shtIBTZmtTu5NkQ/Etw9jUT03SuTOyo702+6l\nEGuiM+71qHWdm8VhubRaXYBSAtq59yWmavUypccSpcefA9+bD8qP90FsQpTPYRvx\n03XS/+Jgd+SFQeKpARxqstBHdq2k0QczY7KHsG3rD/Rvps+CawzjcIF5+S07ROY1\nyqH9utnhlVTVc3XQaGR2AbdOcAnXG+kuD3LREXR84EJc9Ikt5B7rb8kD7GMZ7SX5\ntwwxvBX072cmJxHX5PdLnrRMTod5I+vRHwzsf1mrgQKBgQDWKBDsm/7jhpf7wcFk\n1xi25da5MSZAntEMcwDhmCnrxMWPI/2GmD5UTUj2hjdcLOQJRe2YPkOqiO66YVVE\naYdtOJj8E6j4wNaosTe4wLWRg5grsv/rB4GypEG6cQO0Vfx5q0cs88molGUnxgwA\nJevdJSG6cfsZL9Ax1tqUjkuAQQKBgQC79/lRegJbNR2ITbupQRBt25MUTXLkwSYT\nZ7w7BNPJKsQysAY0SjVmL/dMBiunvQkYyHqP4EKvhTPTjubhqLdgtA1rmamtNmj0\n7RgnzpUojRvT74UIL9sfEbc7+lGbvvRQyfu72UzoG1GXZQ1yVFckHRGxIScvH36n\nCJA0oaSwVwKBgHGqElGC+mYIqeIVlG/ROmzY0H66d3MU2B+janRSLu3UIoc2svkd\nFPfpjTBLTFa//MhvNQv5ADEjPJHv1zHYUOjHgWtJhAWDVGt0o/6LSdNR5RJMj0hP\nU6ddRwWNtkmg2cA6CCzzt7SiDo5trzDk76sQajZrCLr1haruPlVasPgBAoGACQR0\naXw48Lczm35fKld8ukh2Xdr5UBAUC4pGdW5d2qC6mNPo+Ek3FpfmfTcukPV4oj+7\n4XsYt+LkAZoxaVH2uiTpH+hXQ4AAuP9G0WIPtcpPM3OiJiplkLAA4le34ojen6GQ\n+goKrnfhCipG4t048PqUBrNYdeJE6S53/I5koDECgYAy3DCd1Js2vAWbYsAIRn+e\nshLyyiFAbKiJZRlYTOi24Ha1ac71vjtCewMqJrNmdd3GR/oQ9FEMm7wTWKQspsVH\nQ4Q9HYWr/ic3NGUeGUXhBdlyQrwGHIqNUfZwKuXBQlpdKtM1zwe3oWhcclx/EN+H\nc8hEoW96Y/oT4SR8fLQhOg==\n-----END PRIVATE KEY-----\n",
  "client_email": "my-stt-sa@speechtotext-296213.iam.gserviceaccount.com",
  "client_id": "116193986166709937799",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/my-stt-sa%40speechtotext-296213.iam.gserviceaccount.com"
}
"""
try:
    # print("a")
    print("Google Cloud Speech thinks you said " + r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS, language="zh-TW"))
except sr.UnknownValueError:
    print("Google Cloud Speech could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Cloud Speech service; {0}".format(e))
