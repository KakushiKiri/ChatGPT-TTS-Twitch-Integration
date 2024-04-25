from speech_to_text_async import Azure_Manager
from openai_chat import AI_Manager
import asyncio
import time
import keyboard

AI = AI_Manager()
AZURE = Azure_Manager()

while True:
    if keyboard.is_pressed('/'):
        print('Listening to Mic -- Press Q to End')
        message = asyncio.run(AZURE.continuous_mic_input())
        print(f'Here is Your Message: {message}\n--- End Mic Input ---')
        print(f'AI Response: {AI.handle_input(message)}')
    
    time.sleep(0.1)

    if keyboard.is_pressed('f'):
        exit('Goodbye!')