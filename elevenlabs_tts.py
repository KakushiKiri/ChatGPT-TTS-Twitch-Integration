from os import getenv, getcwd
from os.path import join
from elevenlabs.client import ElevenLabs
from elevenlabs import save

class TTS_Manager:
    def __init__(self):
        self.client = ElevenLabs(api_key=getenv('ELEVENLABS_API_KEY'))
        self.voices = self.client.voices.get_all()
        self.main_voice = 'Dave'

    def file_tts(self, input, file_name='current_line.wav'):
        audio = self.client.generate(
            text = input,
            voice = self.main_voice,
            model = 'eleven_multilingual_v2'
        )
        dir = join(getcwd(), file_name)
        save(audio, dir)
if __name__ == '__main__':
    tts = TTS_Manager()
    tts.file_tts('Hello, my name is Dave.')