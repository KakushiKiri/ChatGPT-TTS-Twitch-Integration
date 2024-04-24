import os
import json
import tiktoken
from openai import OpenAI, AuthenticationError

class AI_Manager:
    #class initializer; contains a list and OpenAI instance
    def __init__(self):
        self.conv_history = list()
        self.full_history = list()
        self.token_count = 0
        try:
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        except AuthenticationError:
            exit('ERROR -- You Dummy, you have the wrong OpenAI API Key')

    #check_tokens; Checks the tokens of an input, raises an error if it exceeds limit
    def check_tokens(self, input):
        encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
        if len(encoding.encode(input)) <= 4096:
            self.token_count += len(encoding.encode(input))
        else:
            raise ValueError('ERROR -- Given Prompt Exceeds Token Limit')

    #handle_input; takes prompt as parameter
    def handle_input(self, prompt):
        #check tokens of input, if it passes append to both history variables
        self.check_tokens(prompt)
        self.conv_history.append({'role': 'user', 'content': prompt})
        self.full_history.append({'role': 'user', 'content': prompt})

        #check current token count and conv_history length; begin deleting list elements if either checks pass
        if self.token_count > 13000 or len(self.conv_history) > 20:
            while len(self.conv_history) > 20 or self.token_count > 13000:
                encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
                self.token_count -= len(encoding.encode(self.conv_history[1]['content']))
                del self.conv_history[1]

        #send API request to OpenAI; you may change model if you have access but other parts of code might need changing
        prepare = self.client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=self.conv_history
        )

        #similar to the question, retrieve the response and append to the conversation history, then return response
        response =  prepare.choices[0].message.content
        self.conv_history.append({'role': 'assistant', 'content': response})
        self.full_history.append({'role': 'assistant', 'content': response})

        return response
    
    #set_behavior; no parameters as it should only be used if 'behavior.txt' is present
    def set_behavior(self):
        #check if file is present, else raise FileNotFoundError
        if os.path.isfile('behavior.txt'):
            with open('behavior.txt', 'r') as fname:    #open file and store contents in variable; then call handle_input with said variable
                behavior = fname.read().strip()
            self.check_tokens(behavior)
            self.conv_history.append({'role': 'user', 'content': behavior})
        else:
            raise FileNotFoundError('ERROR -- No Behavior File Found')
    
    #dump_history; if program breaks, the conversation history will be dumped into a file
    def dump_history(self):
        with open('backup_history.json', 'w+') as fname:
            json.dump(self.full_history, fname)


# Use this to test only this file
if __name__ == '__main__':
    ai_test = AI_Manager()
    ai_test.set_behavior()
    print("Welcome to the ChatGPT API test!!\nInput whatever questions you have and/or type 'exit' to end the chat!\n")
    while True:
        question = input('What Question do you Have?: ')
        if question == 'exit' or question == 'Exit':
            break
        elif question == 'tokens' or question == 'Tokens':
            print(f'\n{ai_test.token_count}\n')
        elif question == 'history' or question == 'History':
            for i in ai_test.conv_history:
                print(f'{i["role"]}: {i["content"]}')
        elif question == 'dump' or question == 'Dump':
            ai_test.dump_history()
            break
        else:
            print(f'\n{ai_test.handle_input(question)}\n')