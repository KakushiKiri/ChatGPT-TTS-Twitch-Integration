import os
import keyboard
import azure.cognitiveservices.speech as speech
import time
import queue

class Azure_Manager:
    def __init__(self, speech_queue):
        """initialized Microsoft Azure client for use
        
           param: speech_queue shared queue between Azure_Manager and Thread_Manager

           init: audio_config -- sets up configuration to use the systems default microphone
                 speech_recognizer -- initializes the Microsoft recognizer object for Speech-to-Text
                 audio_config_out -- sets up output to use the systems default output
                 speech_synth -- initializes Microsoft synthesizer for Text-to-Speech
        """
        try:
            self.speech_config = speech.SpeechConfig(subscription=os.getenv('AZURE_API_KEY'), region=os.getenv('AZURE_REGION'))
            self.speech_config.speech_recognition_language = 'en-US'
            self.speech_config.set_profanity(speech.ProfanityOption.Raw)
        except:
            exit('ERROR -- You Dummy, you have the wrong Azure API Key')

        self.audio_config = speech.AudioConfig(use_default_microphone=True)
        self.speech_recognizer = speech.SpeechRecognizer(speech_config=self.speech_config, audio_config=self.audio_config)

        self.audio_config_out = speech.audio.AudioOutputConfig(use_default_speaker=True)
        self.speech_synth = speech.SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.audio_config_out)

        self.speech_queue = speech_queue

    def mic_input(self):
        """listens to microphone a single time for speech-to-text
        
           no param
        """
        print('Listening to Microphone:')
        result = self.speech_recognizer.recognize_once_async.get()

        if result.reason == speech.ResultReason.RecognizedSpeech:
            print(f"You're Message: {result.text}")
        elif result.reason == speech.ResultReason.NoMatch:
            print(f'No Speech Could be Recognized: {result.no_match_details}')
        elif result.reason == speech.ResultReason.Canceled:
            print(f'Mic Input Cancelled: {result.cancellation_details.reason}')

    def continuous_mic_input(self, end_key='q', sync=True):
        """similar to mic_input, but continuously listens to microphone until user stops it

           param: end_key -- key used to end the recognition
                  sync -- determines whether async or sync version is used
        """

        #initialize message for appending and boolean value for loop
        message = ""
        done = False

        #in the case that the session is cancelled, this method will be done
        def stop_cb(evt):
            print(f'Session Ended: {evt}')
            self.speech_recognizer.stop_continuous_recognition()

        #after each recognized input, it will print what you said and append it into the full message
        def compile_lines(evt):
            print(f'Recognized: {evt.result.text}')
            nonlocal message
            message += (evt.result.text + " ")

        self.speech_recognizer.canceled.connect(stop_cb) #connect stop_cb to the canceled event flag
        self.speech_recognizer.recognized.connect(compile_lines) #connect compile_lines to the recognized event flag

        #begin continuous recognition and loop while the check is False
        if sync:
            self.speech_recognizer.start_continuous_recognition()
            print('--- Now Listening to Mic ---')
            while not done:
                if keyboard.is_pressed(end_key):
                    done = True
                time.sleep(0.1)
            self.speech_queue.put(message, block=False)
            self.speech_recognizer.stop_continuous_recognition()
        else:
            self.speech_recognizer.start_continuous_recognition_async()
            print('--- Now Listening to Mic ---')
            while not done:
                if keyboard.is_pressed(end_key):
                    done = True
                time.sleep(0.1)
            self.speech_queue.put(message, block=False)
            self.speech_recognizer.stop_continuous_recognition_async()

    def azure_tts(self, input):
        """basic Text-to-Speech function
        
           param: input -- input to be spoken via TTS
        """
        print('Beginning TTS')
        self.speech_synth.speak_text(input)
        print('TTS Ended')
    
if __name__ == '__main__':
    stt = Azure_Manager(queue.Queue(5))
    print("Welcome to the Azure_Manager Test!\nSelect from the following: ")
    while True:
        print("1. Asynchronous Recognition\n2. Synchronous Recognition\n3. Text-to-Speech\n4. Exit")
        choice = input("Input Choice: ")
        if choice == '1':
            print('Starting Async Recognition || Press Q to end')
            stt.continuous_mic_input(sync=False)
            print(stt.speech_queue.get())
        elif choice == '2':
            print('Starting Sync Recognition || Press Q to end')
            stt.continuous_mic_input()
            print(stt.speech_queue.get())
        elif choice == '3':
            temp = input('What would you like to be said in Text-to-Speech?: ')
            stt.azure_tts(temp)
        elif choice == '4':
            exit('Have a Nice Day!')
        else:
            print('Invalid Choice :( Please Try Again\n')