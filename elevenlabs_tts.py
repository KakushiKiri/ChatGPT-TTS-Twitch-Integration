from os import getenv, getcwd, remove
from time import sleep
from asyncio import wait, run
from os.path import join
from elevenlabs.client import ElevenLabs, AsyncElevenLabs
from elevenlabs import save, stream, play
from playsound import playsound
from mutagen.mp3 import MP3

class TTS_Manager:
    def __init__(self, sync=True):
        if sync:
            self.client = ElevenLabs(api_key=getenv('ELEVENLABS_API_KEY'))
        else:
            self.client = AsyncElevenLabs(api_key=getenv('ELEVENLABS_API_KEY'))
        self.voices = self.client.voices.get_all()
        self.main_voice = 'Dave'

    def file_length(self, file):
        audio = MP3(file)
        return audio.info.length

    def play_file(self, file):
        dir = join(getcwd(), file)
        playsound(dir)
        remove(dir)

    async def file_tts(self, input, file_name='current_line.mp3'):
        audio = self.client.generate(
            text = input,
            voice = self.main_voice,
            model = 'eleven_multilingual_v2'
        )
        dir = join(getcwd(), file_name)
        save(audio, dir)
    
    def stream_tts(self, input):
        audio_stream = self.client.generate(
            text=input,
            stream=True
        )
        stream(audio_stream)
        
if __name__ == '__main__':
    tts = TTS_Manager(True)

    tts.stream_tts("How is it going, my name is john dark souls.")

    # run(tts.file_tts("Hello, my name is Dave"))
    # dir = join(getcwd(), 'current_line.mp3')
    # tts.play_file(dir)