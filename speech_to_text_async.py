import os
import asyncio
import keyboard
import azure.cognitiveservices.speech as speech

#azure_manager; contains the initializer, audio_config, speech_recognizer, and a check variable used by the continuous method
class Azure_Manager:
    def __init__(self):
        try:
            self.speech_config = speech.SpeechConfig(subscription=os.getenv('AZURE_API_KEY'), region=os.getenv('AZURE_REGION'))
            self.speech_config.speech_recognition_language = 'en-US'
        except:
            exit('ERROR -- You Dummy, you have the wrong Azure API Key')

        self.speech_config = speech.ProfanityOption(self.speech_config.set_profanity('Raw'))
        
        self.audio_config = speech.AudioConfig(use_default_microphone=True)
        self.speech_recognizer = speech.SpeechRecognizer(speech_config=self.speech_config, audio_config=self.audio_config)

        self.continuous_check = False

    #mic_input; reads from microphone a single time, listening for a maximum of 15 seconds OR until silence
    def mic_input(self):        
        print('Listening to Microphone:')
        result = self.speech_recognizer.recognize_once_async.get()

        if result.reason == speech.ResultReason.RecognizedSpeech:
            print(f"You're Message: {result.text}")
        elif result.reason == speech.ResultReason.NoMatch:
            print(f'No Speech Could be Recognized: {result.no_match_details}')
        elif result.reason == speech.ResultReason.Canceled:
            print(f'Mic Input Cancelled: {result.cancellation_details.reason}')

    #continuous_mic_input; reads from mic until user input, appending each input into one large message
    async def continuous_mic_input(self, end_key='q'):
        message = ""
        done = False
        #in the case that the session is cancelled, this method will be done
        def stop_cb(evt):
            print(f'Session Ended: {evt}')
            self.speech_recognizer.stop_continuous_recognition()
            nonlocal done
            done = True

        #after each recognized input, it will print what you said and append it into the full message
        def compile_lines(evt):
            print(f'Recognized: {evt.result.text}')
            nonlocal message
            message += (evt.result.text + " ")

        self.speech_recognizer.canceled.connect(stop_cb) #connect stop_cb to the canceled event flag
        self.speech_recognizer.recognized.connect(compile_lines) #connect compile_lines to the recognized event flag4

        #begin continuous recognition and loop while the check is False
        self.speech_recognizer.start_continuous_recognition_async()
        print('--- Now Listening to Mic ---')
        while not done:
            if keyboard.is_pressed(end_key):
                done = True
        self.speech_recognizer.stop_continuous_recognition_async()
        
        #return final message
        return message.strip()

    async def test_message(self):
        result = await self.continuous_mic_input()
        return result

if __name__ == '__main__':
    stt = Azure_Manager()
    message = asyncio.run(stt.test_message())
    print(message)