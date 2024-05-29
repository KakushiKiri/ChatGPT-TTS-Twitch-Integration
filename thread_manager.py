from openai_chat import AI_Manager
# from elevenlabs_tts import TTS_Manager
from speech_to_text import Azure_Manager
from vad_manager import VAD_Manager
from threading import Thread, Event
import keyboard
import time
import numpy as np
import queue
import torch

class Thread_Manager():
    def __init__(self):
        """initialized Thread_Manager to encompass the main logic of the program
        
           no params

           init: speech_queue, tts_queue -- queue's shared between Thread_Manager and Azure_Manager/AI_Manager respectively
                 found_speech -- Thread event for the VAD to signal the start of the Speech-to-Text
                 pause_vad -- Thread event for the VAD to pause after Speech-to-Text is finished

                 AI, STT, VAD -- Three main classes imported from their respective files

                 vad/ai/recognition/tts_thread -- variables that threads will be assigned to
        """
        self.speech_queue = queue.Queue(5)
        self.tts_queue = queue.Queue(5)

        self.found_speech = Event()
        self.pause_vad = Event()
        
        self.AI = AI_Manager(self.tts_queue)
        self.STT = Azure_Manager(self.speech_queue)
        self.VAD = VAD_Manager()

        self.vad_thread = Thread(target=self.VAD_Thread)
        self.ai_thread = Thread(target=self.AI_Thread)
        self.recognition_thread = Thread(target=self.Recognition_Thread)
        self.tts_thread = Thread(target=self.TTS_Thread)

        self.thread_list = [self.vad_thread, self.recognition_thread, self.ai_thread, self.tts_thread]

    def VAD_Thread(self):
        """same logic as vad_manager.py
        
           no params
        """
        stream = self.VAD.audio.open(format=self.VAD.FORMAT,
                        channels=self.VAD.CHANNELS,
                        rate=self.VAD.SAMPLE_RATE,
                        input=True,
                        frames_per_buffer=self.VAD.CHUNK)

        while True:
            audio_chunk = stream.read(self.VAD.num_samples)
            audio_int16 = np.frombuffer(audio_chunk, np.int16)
            audio_float32 = self.VAD.int2float(audio_int16)

            new_confidence = self.VAD.model(torch.from_numpy(audio_float32), 16000).item()
            if not self.found_speech.is_set():
                if new_confidence >= 0.6:
                    self.found_speech.set()
    
    def Recognition_Thread(self):
        """waits for event from VAD_Thread, then runs continuous mic input
           clears found_speech event to loop and wait again

           no params
        """
        while True:
            self.found_speech.wait()
            self.STT.continuous_mic_input()
            self.found_speech.clear()

    def AI_Thread(self):
        """does not rely on an event, but will be in a sleeping state until an item is in the speech_queue
           it then sends it to the AI to process
        
           no params
        """
        while True:
            if not self.speech_queue.empty():
                self.AI.handle_input(self.speech_queue.get())
            time.sleep(0.1)

    def TTS_Thread(self):
        """similar to AI_Thread, sleeps until item is in tts_queue, plays audio, and then resumes VAD

           no params
        """
        while True:
            if not self.tts_queue.empty():
                self.STT.azure_tts(self.tts_queue.get())
                self.pause_vad.set()
            time.sleep(0.1)

    def Create_Threads(self):
        """loops through thread_list and starts each one
        
           no params
        """
        for thread in self.thread_list:
            thread.start()
    
    def stop_threads(self):
        """loops through thread_list and ends each one
        
           no params
        """
        for thread in self.thread_list:
            thread.join(timeout=0.5)
        self.VAD.audio.terminate()

if __name__ == '__main__':
    Threads = Thread_Manager()
    Threads.Create_Threads()
    running = True
    while running:
        if keyboard.is_pressed('p'):
            Threads.stop_threads()
            running = False