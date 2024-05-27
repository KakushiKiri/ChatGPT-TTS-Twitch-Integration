from openai_chat import AI_Manager
from elevenlabs_tts import TTS_Manager
from speech_to_text import Azure_Manager
from vad_manager import VAD_Manager
from threading import Thread
import keyboard
import time
import numpy as np
import queue
import torch

class Thread_Manager():
    def __init__(self):
        self.speech_queue = queue.Queue(5)
        self.tts_queue = queue.Queue(5)
        self.found_speech = False
        self.pause_vad = False
        self.finished = True

        self.continue_recording = True

        self.AI = AI_Manager(self.tts_queue)
        self.TTS = TTS_Manager()
        self.STT = Azure_Manager(self.speech_queue)
        self.VAD = VAD_Manager()

        self.vad_thread = None
        self.ai_thread = None
        self.recognition_thread = None
        self.tts_thread = None

    def VAD_Thread(self):
        stream = self.VAD.audio.open(format=self.VAD.FORMAT,
                        channels=self.VAD.CHANNELS,
                        rate=self.VAD.SAMPLE_RATE,
                        input=True,
                        frames_per_buffer=self.VAD.CHUNK)

        while self.continue_recording:
            audio_chunk = stream.read(self.VAD.num_samples)
            audio_int16 = np.frombuffer(audio_chunk, np.int16)
            audio_float32 = self.VAD.int2float(audio_int16)

            # get the confidences
            new_confidence = self.VAD.model(torch.from_numpy(audio_float32), 16000).item()
            #print(new_confidence)
            if new_confidence >= 0.6:
                stream.stop_stream()
                self.found_speech = True
                self.pause_vad = True
                while self.pause_vad:
                    time.sleep(0.1)
                stream.start_stream()
        stream.stop_stream()
        self.VAD.audio.terminate()
        print('Stopped Recording')
    
    def Recognition_Thread(self):
        while not self.finished:
            if self.found_speech:
                self.STT.continuous_mic_input(sync=True)
                self.found_speech = False
                self.pause_vad = False
            time.sleep(0.1)

    def AI_Thread(self):
        while not self.finished:
            if not self.speech_queue.empty():
                self.AI.handle_input(self.speech_queue.get())
                self.pause_vad = False
            time.sleep(0.1)

    def TTS_Thread(self):
        while not self.finished:
            if not self.tts_queue.empty():
                self.TTS.stream_tts(self.tts_queue.get())
            time.sleep(0.1)

    def Create_Threads(self):
        self.vad_thread = Thread(target=self.VAD_Thread)
        self.recognition_thread = Thread(target=self.Recognition_Thread)
        self.ai_thread = Thread(target=self.AI_Thread)
        self.tts_thread = Thread(target=self.TTS_Thread)

        self.vad_thread.start()
        self.recognition_thread.start()
        self.ai_thread.start()
        self.tts_thread.start()
    
    def stop_threads(self):
        self.finished = True
        self.vad_thread.join(timeout=0.5)
        self.ai_thread.join(timeout=0.5)
        self.recognition_thread.join(timeout=0.5)
        self.tts_thread.join(timeout=0.5)
        self.VAD.audio.terminate()

if __name__ == '__main__':
    Threads = Thread_Manager()
    # if not Threads.finished:
    Threads.finished = False
    Threads.Create_Threads()
    while not Threads.finished:
        if keyboard.is_pressed('p'):
            Threads.stop_threads()