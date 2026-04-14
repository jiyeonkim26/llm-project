import json
import os
from groq import Groq
from tools.calculate import calculate, tool_schema

from dotenv import load_dotenv
load_dotenv()

# in python class names are in CamelCase:
# non-class names (e.g. function/variable) are in snake_case:
class Chat:
   '''
   >>> def monkey_input(prompt, user_inputs=['Hello, I am monkey.', 'Goodbye.']):
   ...    try:
   ...        user_input = user_inputs.pop(0)
   ...        print(f'{prompt}{user_input}')
   ...        return user_input
   ...    except IndexError:
   ...        raise KeyboardInterrupt
   >>> import builtins
   >>> builtins.input = monkey_input
   >>> repl(temperature=0.0)
   chat> Hello, I am monkey.
   Nice to meet you, monkey! How can I help you today?
   chat> Goodbye.
   Goodbye! Feel free to return anytime you need assistance.
   <BLANKLINE>
   '''
   '''
   >>> chat = Chat()
   >>> chat.send_message('my name is Bob', temperature=0.0)
   "Hello Bob, it's nice to meet you."
   >>> chat.send_message('what is my name?', temperature=0.0)
   'Your name is Bob.'


   >>> chat2 = Chat()
   >>> chat2.send_message('what is my name?', temperature=0.0)
   "I don't have any information about your name. I'm a text-based AI assistant and our conversation just started, so I don't have any prior knowledge about you."
   '''
   client = Groq(api_key=os.getenv("GROQ_API_KEY"))
   MODEL="openai/gpt-oss-120b"
   def __init__(self):
       self.messages = [
           {
               "role": "system",
               "content": "Write the output in 1-2 sentences. Always use tools to complete tasks when appropriate. Don't bold the answer."
           },
       ]
   def send_message(self, message, temperature=0.8):
       self.messages.append(
           {
               # system: never change; user: changes a lot
               # the message that you are sending to the AI
               'role': 'user',
               'content': message
           }
       )
       # define tools
       tools = [tool_schema]


       # in order to make non deterministic code deterministic:
       # in this case, has a 'temperature' param that controls randomness:
       # the higher the value, the more randomness;
       # higher temperature = more creativity
       chat_completion = self.client.chat.completions.create(
           messages=self.messages,
           # model="llama-3.1-8b-instant",
           model = self.MODEL,
           temperature=temperature,
           seed=0,
           tools=tools,
           tool_choice="auto"
       )


       response_message = chat_completion.choices[0].message
       tool_calls = response_message.tool_calls
      
       # Step 2: Check if the model wants to call tools
       if tool_calls:
           # Map function names to implementations
           available_functions = {
               "calculate": calculate,
           }

           # Add the assistant's response to conversation
           self.messages.append(response_message)

           # Step 3: Execute each tool call
           for tool_call in tool_calls:
               function_name = tool_call.function.name
               function_to_call = available_functions[function_name]
               function_args = json.loads(tool_call.function.arguments)
               function_response = function_to_call(
                   expression=function_args.get("expression")
               )
               print(f'[tool] function_name={function_name}, function_args={function_args}')


               # Add tool response to conversation
               self.messages.append({
                   "tool_call_id": tool_call.id,
                   "role": "tool",
                   "name": function_name,
                   "content": function_response,
               })
          
           # Step 4: Get final response from model
           second_response = self.client.chat.completions.create(
               model= 'openai/gpt-oss-120b',
               messages= self.messages
           )
           result = second_response.choices[0].message.content
           self.messages.append({
               'role': 'assistant',
               'content': result
           })
       # tell LLM what we were previously talking about
       else:
           result = chat_completion.choices[0].message.content
           self.messages.append({
               'role': 'assistant',
               'content': result
           })
       return result


# this makes the user interface nicer by saying 'chat>'
# repl: reads input and evaluates input
'''
if __name__ == '__main__':
   chat = Chat()
   try:
       while True:
               user_input = input('chat>')
               response = chat.send_message(user_input)
               print(response)
   except KeyboardInterrupt:
       print()
'''


def repl(temperature=0.0):
   import readline
   chat = Chat()
   try:
       while True:
           user_input = input('chat> ')
           response = chat.send_message(user_input, temperature=temperature)
           print(response)
   except (KeyboardInterrupt, EOFError):
       print()


if __name__ == '__main__':
   repl()
