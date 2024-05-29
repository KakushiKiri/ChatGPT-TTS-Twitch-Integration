import os
import json
import tiktoken
import queue
from openai import OpenAI, AuthenticationError

class AI_Manager:
    #handles max length of conversation list
    CONV_LEN = 21

    def __init__(self, ai_queue):
        """initializes AI usage

        param: ai_queue -- shared queue between AI_Manager and Thread_Manager
        
        init: conv_history -- temporary history of conversation up to CONV_LEN in length
              full_history -- full conversation history for use of backups
              token_count -- keeps track of total amount of tokens in con_history
              ai_queue -- queue in which AI responses are put
        """
        self.conv_history = list()
        self.full_history = list()
        self.token_count = 0
        try:
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        except AuthenticationError:
            exit('ERROR -- You Dummy, you have the wrong OpenAI API Key')

        self.ai_queue = ai_queue

    @classmethod
    def set_conv_len(cls, amt):
        """sets class variable CONV_LEN to new amount

        param: amt -- amount to change CONV_LEN to
        """
        cls.CONV_LEN = amt

    def append_conv(self, role, content):
        """appends user input and/or AI response to conv_history and full_history
    
        param: role -- either 'user' or 'assistant'
               content -- users input or AI's response    
        """
        self.conv_history.append({'role': role, 'content': content})
        self.full_history.append({'role': role, 'content': content})       

    def check_tokens(self, input):
        """checks tokens of a given input, raises error if token amount is too high, otherwise adds to class token_count
        
        param: input -- user or AI's input
        """
        encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
        if len(encoding.encode(input)) <= 4096:
            self.token_count += len(encoding.encode(input))
        else:
            raise ValueError('ERROR -- Given Prompt Exceeds Token Limit')

    def handle_input(self, prompt, stream=False):
        """handles user input and generates the AI's response

        param: prompt -- input from user
               stream -- determines whether AI streams it's response in chunks (defaults to False)
        """
        #check tokens of input, if it passes append to both history variables
        self.check_tokens(prompt)
        self.append_conv('user', prompt)

        #check current token count and conv_history length; begin deleting list elements if either checks pass
        if self.token_count > 13000 or len(self.conv_history) > self.CONV_LEN:
            while len(self.conv_history) > 20 or self.token_count > 13000:
                encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
                self.token_count -= len(encoding.encode(self.conv_history[1]['content']))
                del self.conv_history[1]

        #send API request to OpenAI; you may change model if you have access but other parts of code might need changing
        print('Beginning Response Generation')
        if not stream:
            prepare = self.client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=self.conv_history
            )
            print('Response Generated')
            response =  prepare.choices[0].message.content
            self.ai_queue.put(response, block=False)
        else:
            response = ''
            stream = self.client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=self.conv_history,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    response += chunk.choices[0].delta.content
            self.ai_queue.put(response, block=False)

        #similar to the question, retrieve the response and append to the conversation history
        self.append_conv('assistant', response)
        self.check_tokens(response)  

    def set_behavior(self):
        """sets behavior of the ai by placing contents of 'behavior.txt' in conv_history[0]

           no param
        """
        #check if file is present, else raise FileNotFoundError
        if os.path.isfile('behavior.txt'):
            with open('behavior.txt', 'r') as fname:    #open file and store contents in variable; then call handle_input with said variable
                behavior = fname.read().strip()
            if len(behavior) != 0:
                self.check_tokens(behavior)
                self.conv_history.append({'role': 'user', 'content': behavior})
        else:
            return "No Behavior File Present"
    
    def dump_history(self):
        """dumps full_history to json file
        
           no param
        """
        with open('backup_history.json', 'w+') as fname:
            json.dump(self.full_history, fname)


# Use this to test only this file
if __name__ == '__main__':
    ai_test = AI_Manager(queue.Queue(5))
    ai_test.set_behavior()
    print("Welcome to the ChatGPT API test!!")
    while True:
        print("Ask a question or type one of the following:\n1. tokens\n2. history\n3. dump\n4. exit")
        question = input('What Question do you Have?: ')
        if question.lower() == 'exit':
            exit('Thank you for testing!')
        elif question.lower() == 'tokens':
            print(f'\n{ai_test.token_count}\n')
        elif question.lower() == 'history':
            for i in ai_test.conv_history:
                print(f'{i["role"]}: {i["content"]}')
        elif question.lower() == 'dump':
            ai_test.dump_history()
            break
        else:
            ai_test.handle_input(question)
            print(ai_test.ai_queue.get())