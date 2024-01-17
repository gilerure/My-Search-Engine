# -*- coding: utf-8 -*-
from time import sleep

CACHE_FILE_PATH = "Group_Task/cache/chat_input.txt"
OUTPUT_FILE_PATH = "Group_Task/cache/chat_output.txt"
ATTRS_FILE_PATH = "Group_Task/cache/chat_attrs.txt"

def read_output():
    file = open(OUTPUT_FILE_PATH, 'r', encoding='utf-8')
    output = file.read()
    file.close()
    return output

def read_attrs():
    file = open(ATTRS_FILE_PATH, 'r', encoding='utf-8')
    attrs = file.readlines()
    for i in range(len(attrs)):
        attrs[i] = attrs[i].replace('\n', '')
    file.close()
    return attrs

def write_input(command):
    file = open(CACHE_FILE_PATH, 'w', encoding='utf-8')
    file.write(command)
    file.close()

while(True):
    command = input("Enter command: ")
    write_input(command)
    while read_output() == '':
        print("waiting for output...")
        sleep(1)
        pass
    print("output: ", read_output())
    print("attrs: ", read_attrs())