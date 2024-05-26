from openai_chat import AI_Manager
from elevenlabs_tts import TTS_Manager
from speech_to_text import Azure_Manager
from vad_manager import VAD_Manager
import time
import numpy as np
import queue
import torch

class Thread_Manager():
    def __init__(self):
        self.speech_queue = queue.Queue(5)
        self.found_speech = False
        self.AI = AI_Manager()
        self.TTS = TTS_Manager()
        self.STT = Azure_Manager(self.speech_queue)
        self.VAD = VAD_Manager()

    def VAD_Thread(self):
        stream = self.VAD.audio.open(format=self.VAD.FORMAT,
                        channels=self.VAD.CHANNELS,
                        rate=self.VAD.SAMPLE_RATE,
                        input=True,
                        frames_per_buffer=self.VAD.CHUNK)
        continue_recording = True

        while continue_recording:
            audio_chunk = stream.read(self.VAD.num_samples)
            audio_int16 = np.frombuffer(audio_chunk, np.int16)
            audio_float32 = self.VAD.int2float(audio_int16)

            # get the confidences
            new_confidence = self.VAD.model(torch.from_numpy(audio_float32), 16000).item()
            print(new_confidence)
            if new_confidence >= 0.8:
                stream.stop_stream()
                self.found_speech = True
                self.STT.continuous_mic_input(sync=True)
                print(self.speech_queue.empty())
            while self.found_speech:
                time.sleep(0.1)
        print('Stopped Recording')

Threads = Thread_Manager()
Threads.VAD_Thread()