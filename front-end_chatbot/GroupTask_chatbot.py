# -*- coding: utf-8 -*-
import re
from translate import Translator
from gpt4all import GPT4All
from time import sleep


MODEL_PATH = "F:\sjtu\gpt4all-falcon-q4_0.gguf"
# the model you downloaded (.gguf file)

model = GPT4All(MODEL_PATH, allow_download=False)
print("model retrieved!")

prompt0 = "Now you are a customer assistant of an EC platform selling clothings."
prompt1 = "From now on, I will give requests of the customers, and you must make out what kind of clothing they want. Then conclude keywords of the target clothing, and print no more than 5 keywords."
prompt2 = "request: 'I am looking for a pair of shoes that is warm to wear in winter. Also it should be lightweight.'"
prompts = [prompt0, prompt1, prompt2]

# main task: conclude the key words of the request, like clothing type, color, size, gender, brand, etc.
# display the search result of the keywords

    
def translate(text, src='en', tgt='zh'):
    text = Translator(from_lang=src, to_lang=tgt).translate(text)
    return text

def search_attributions(text):
    pattern = re.compile(r'\.(.*?)\n')
    attributions = pattern.findall(text)
    for i in range(len(attributions)):
        attributions[i] = attributions[i] + '\n'
    return attributions

def generate(model, hint, max_tokens=2, temp=0):
    t = temp
    outp = model.generate(hint, max_tokens, n_batch=256, temp=t)
    print(outp)

def chat(model, hints, max_tokens=200, temp=0):
    
    CACHE_FILE_PATH = "F:\sjtu\电工导C\电工导大作业\search\cache\chat_input.txt"
    OUTPUT_FILE_PATH = "F:\sjtu\电工导C\电工导大作业\search\cache\chat_output.txt"
    ATTRS_FILE_PATH = "F:\sjtu\电工导C\电工导大作业\search\cache\chat_attrs.txt"

    # cache file. read from it pre 1 second. if has content, use it as input, and clear it.

    with model.chat_session():
        # prompts
        for hint in hints:
            outp = model.generate(hint, max_tokens, n_batch=256, temp=temp)
            # print(translate(outp))
        file = open(CACHE_FILE_PATH, 'w', encoding='utf-8')
        file.close()
        print('------------------------------------------------------------------')
        print("")
        while(True):
            file = open(CACHE_FILE_PATH, 'r', encoding='utf-8', errors='ignore')
            output_file = open(OUTPUT_FILE_PATH, 'w', encoding='utf-8')
            attrs_file = open(ATTRS_FILE_PATH, 'w', encoding='utf-8')
            command = file.read()
            while(command == ''):
                sleep(1)
                print("waiting for input...")
                file = open(CACHE_FILE_PATH, 'r', encoding='utf-8', errors='ignore')
                command = file.read()
            print("command: " + command)
            hint = command
            file = open(CACHE_FILE_PATH, 'w', encoding='utf-8')
            file.write('')
            file.close()
            if hint == 'exit':
                break
            outp = model.generate('request: ' + translate(hint, src='zh', tgt='en'), max_tokens, n_batch=256, temp=temp)
            outp = translate(outp)
            output_file.write(outp + '\n')
            attributions = search_attributions(outp + '\n')
            attrs_file.writelines(attributions)
            print(outp)
            print(attributions)
        print("chat session ended!")

def chat_without_cache(model, hints, max_tokens=200, temp=0):
    with model.chat_session():
        # prompts
        for hint in hints:
            outp = model.generate(hint, max_tokens, n_batch=256, temp=temp)
            # print(translate(outp))

        print('------------------------------------------------------------------')
        print("")
        print(">>> ", end='')
        command = input()
        if command == 'exit':
            return
        hint = command
        outp = model.generate('request: ' + translate(hint, src='zh', tgt='en'), max_tokens, n_batch=256, temp=temp)
        outp = translate(outp)
        attributions = search_attributions(outp + '\n')
        print(outp)
        print(attributions)
        print("chat session ended!")
        return attributions

chat(model, prompts, max_tokens=200, temp=0)

print("chat session ended!")

# the gpt chatbot will generate 5 possible attributions of the request
# then search it through the database to find the most suitable clothing