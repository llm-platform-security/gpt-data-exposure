import json
import os
from os import listdir
from os.path import isfile, join


def read_json(file_addr):
    with open(file_addr) as json_data:
        d = json.load(json_data)
    return d

def write_json(file_name, data, indent_length=4):
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile, indent=indent_length)

def write_list_utf(file_addr, list_content):
    with open(file_addr, 'w') as out_file:
        for item in list_content:
            out_file.write(item.encode('utf-8') + '\n') 

def write_list_simple(file_addr, list_content):
    with open(file_addr, 'w') as out_file:
        for item in list_content:
            out_file.write(item + '\n') 

def write_content(file_addr, content):
    with open(file_addr, 'w') as out_file:        
        out_file.write(content) 

def write_content_bytes(file_addr, content):
    with open(file_addr, 'wb') as out_file:        
        out_file.write(content) 

def append_file(file_name, content):
    with open(file_name, "a") as myfile:
        myfile.write(content + '\n')

def read_file(file_addr):
    with open(file_addr) as f:
        content = f.readlines()
    return content

def read_full_file(file_addr):
    with open(file_addr) as f:
        content = f.read()
    return content

def write_full_file_bytes(file_name, content):
    with open(file_name, "wb") as myfile:
        myfile.write(content)

def write_full_file(file_name, content):
    with open(file_name, "w") as myfile:
        myfile.write(content)

def read_file_newline_stripped(file_path):
    with open(file_path) as f:
        content = [word.strip() for word in f]
    return content


def append_list(file_addr, content):
    with open(file_addr, 'a') as myfile:
        for line in content:
            myfile.write(line + '\n')

def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True

def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b


def get_files_in_a_directory(directory_path):
    file_list = [f for f in listdir(directory_path) if isfile(join(directory_path, f)) and not f.startswith('.')]
    file_list_path = [os.path.join(directory_path, f) for f in file_list]
    return file_list_path


def get_directories_in_a_directory(directory_path):
    file_list = [f for f in listdir(directory_path) if not isfile(join(directory_path, f)) and not f.startswith('.')]
    file_list_path = [os.path.join(directory_path, f) for f in file_list]
    return file_list_path