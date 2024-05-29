import numpy as np
import torch
torch.set_num_threads(1)
import torchaudio
torchaudio.set_audio_backend("soundfile")
import pyaudio

"""
    MIT License

    Copyright (c) 2020-present Silero Team

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""
class VAD_Manager():
    def __init__(self):
        """initializes SileroVAD for use
        
           no param

           init: model/utils -- loaded from torch
                 FORMAT, CHANNELS, SAMPLE_RATE, CHUNK -- values for pyaudio
                 audio -- pyaudio instance
        """
        self.model, self.utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=True)
        (self.get_speech_timestamps,
        self.save_audio,
        self.read_audio,
        self.VADIterator,
        self.collect_chunks) = self.utils

        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.SAMPLE_RATE = 16000
        self.CHUNK = int(self.SAMPLE_RATE / 10)

        self.audio = pyaudio.PyAudio()
        self.num_samples = 1536

    def int2float(self, sound):
        abs_max = np.abs(sound).max()
        sound = sound.astype('float32')
        if abs_max > 0:
            sound *= 1/32768
        sound = sound.squeeze()  # depends on the use case
        return sound

    def start_recording(self):
        """begins recording with the VAD, the closer to 1 the more likely it is speech
           (this is more for testing for now)

           no params
        """
        stream = self.audio.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.SAMPLE_RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        continue_recording = True
        try:
            while continue_recording:
                audio_chunk = stream.read(self.num_samples)
                audio_int16 = np.frombuffer(audio_chunk, np.int16)
                audio_float32 = self.int2float(audio_int16)

                # get the confidences
                new_confidence = self.model(torch.from_numpy(audio_float32), 16000).item()
                print(new_confidence)
        except KeyboardInterrupt:
            exit("Stopped Recording")

if __name__ == '__main__':
    VAD = VAD_Manager()
    VAD.start_recording() 