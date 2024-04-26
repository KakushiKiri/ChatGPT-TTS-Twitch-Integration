from os import getenv, getcwd, remove
from asyncio import wait
from os.path import join
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from playsound import playsound
from mutagen.mp3 import MP3

class TTS_Manager:
    def __init__(self):
        self.client = ElevenLabs(api_key=getenv('ELEVENLABS_API_KEY'))
        self.voices = self.client.voices.get_all()
        self.main_voice = 'Dave'

    def file_length(self, file):
        audio = MP3(file)
        return audio.info.length

    def file_tts(self, input, file_name='current_line.mp3'):
        audio = self.client.generate(
            text = input,
            voice = self.main_voice,
            model = 'eleven_multilingual_v2'
        )
        dir = join(getcwd(), file_name)
        save(audio, dir)
        length = self.file_length(file_name)
        playsound(dir, False)
        wait(int(length) + 2)
        remove(dir)

if __name__ == '__main__':
    tts = TTS_Manager()
    tts.file_tts('Hello, my name is Dave.')