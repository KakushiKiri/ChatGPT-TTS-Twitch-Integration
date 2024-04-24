import os
import keyboard
import subprocess
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

        if result.reason == speech.ResultReason.RecognizedSpeech:
            print(f"You're Message: {result.text}")
        elif result.reason == speech.ResultReason.NoMatch:
            print(f'No Speech Could be Recognized: {result.no_match_details}')
        elif result.reason == speech.ResultReason.Canceled:
            print(f'Mic Input Cancelled: {result.cancellation_details.reason}')

    def continuous_mic_input(self, stop='q'):
        speech_recognizer = speech.SpeechRecognizer(speech_config=self.speech_config, audio_config=self.audio_config)

        done = False
        message = ""
        def stop_cb(evt):
            print(f'Session Ended: {evt}')
            speech_recognizer.stop_continuous_recognition()
            nonlocal done
            done = True

        def compile_lines(evt):
            print(f'Recognized: {evt.result.text}')
            nonlocal message
            message += (evt.result.text + " ")

        speech_recognizer.canceled.connect(stop_cb)
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.recognized.connect(compile_lines)

        result = speech_recognizer.start_continuous_recognition()
        print('--- Now Listening to Mic ---')
        while not done:
            if keyboard.is_pressed(stop):
                print('Test 1')
                speech_recognizer.stop_continuous_recognition()
                print('Test 2')

        print(f'Here is Your Message: {message.strip()}')
        return message.strip()
    
if __name__ == '__main__':
    stt = Azure_Manager()
    stt.continuous_mic_input()