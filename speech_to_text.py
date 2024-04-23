import os
import azure.cognitiveservices.speech as speech

class Azure_Manager:
    def __init__(self):
        try:
            self.speech_config = speech.SpeechConfig(subscription=os.getenv('AZURE_API_KEY'), region=os.getenv('AZURE_REGION'))
            self.speech_config.speech_recognition_language = 'en-US'
        except:
            exit('ERROR -- Oopsies, you have the wrong Azure API Key')

        self.audio_config = speech.AudioConfig(use_default_microphone=True)

    def mic_input(self):
        speech_recognizer = speech.SpeechRecognizer(speech_config=self.speech_config, audio_config=self.audio_config)
        
        print('Listening to Microphone:')
        result = speech_recognizer.recognize_once_async.get()