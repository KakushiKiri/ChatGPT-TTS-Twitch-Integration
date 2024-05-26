from openai_chat import AI_Manager
from elevenlabs_tts import TTS_Manager
from speech_to_text import Azure_Manager
from vad_manager import VAD_Manager
from threading import Thread
import time
import numpy as np
import queue
import torch

class Thread_Manager():
    def __init__(self):
        self.speech_queue = queue.Queue(5)
        self.found_speech = False
        self.pause_vad = False
        self.finished = True

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
                self.pause_vad = True
                while self.pause_vad:
                    time.sleep(0.1)
                stream.start_stream()
        print('Stopped Recording')
    
    def Recognition_Thread(self):
        while not self.finished:
            if self.found_speech:
                self.STT.continuous_mic_input(sync=True)
                self.found_speech = False
            time.sleep(0.1)

    def AI_Thread(self):
        while not self.finished:
            if not self.speech_queue.empty():
                response = self.AI.handle_input(self.speech_queue.get())
                self.TTS.stream_tts(response)
                self.pause_vad = False
            time.sleep(0.1)

    def Create_Threads(self):
        vad_thread = Thread(target=self.VAD_Thread)
        recognition_thread = Thread(target=self.Recognition_Thread)
        ai_thread = Thread(target=self.AI_Thread)

        vad_thread.start()
        recognition_thread.start()
        ai_thread.start()

if __name__ == '__main__':
    Threads = Thread_Manager()
    if not Threads.finished:
        Threads.finished = False
        Threads.Create_Threads()