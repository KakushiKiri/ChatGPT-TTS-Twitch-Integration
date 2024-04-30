from speech_to_text import Azure_Manager
from openai_chat import AI_Manager
from elevenlabs_tts import TTS_Manager
import asyncio
import time
import keyboard

AI = AI_Manager()
AZURE = Azure_Manager()
ELEVENLABS = TTS_Manager()

while True:
    if keyboard.is_pressed('/'):
        print('Listening to Mic -- Press Q to End')
        message = asyncio.run(AZURE.continuous_mic_input(sync=True))
        print(f'Here is Your Message: {message}\n--- End Mic Input ---')
        result = AI.handle_input(message, False)
        print(f'AI Response: {result}')
        asyncio.run(ELEVENLABS.file_tts(result))
        ELEVENLABS.play_file('current_line.mp3')

    time.sleep(0.1)

    if keyboard.is_pressed('f'):
        exit('Goodbye!')