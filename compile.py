import json
import os.path, os
from typing import List

def exclude_imports(text: str, packets: List[str]):
    t2 = ""
    for line in text.splitlines():
        splited = line.split()
        if len(splited) >= 2:
            if splited[0] == 'from':
                if splited[1] in packets: continue
            elif splited[0] == 'import':
                if splited[1] in packets: continue
        for p in packets:
            indx = line.find(p + '.')
            if indx <= 0 or line[indx-1] in "+-=*/( ":
                line = line.replace(p + '.', '') 
        t2 += line + '\n'
    return t2

with open("./.comp", 'r', encoding='utf-8') as file:
    params = json.loads(file.read())

if not os.path.exists(params['build']['dir']):
    os.mkdir(params['build']['dir'])

text = """
##############################################################
# This file was autocompiled and including next files content:"""

for filename in params['packets']:
    text += "\n#\t- " + filename

text += "\n# And the main file: " + params["main"]

text += """
##############################################################
# Next you can see splited files content
"""

for filename in params['packets']:
    text += """##############################################################
# """ + filename + ' file content:\n'
    with open(filename + '.py', 'r', encoding='utf-8') as file:
        text += exclude_imports(file.read(), params["packets"]) + '\n\n'

text += """##############################################################
# """ + params["main"] + """ (MAIN) file content:
"""
with open(params["main"], 'r', encoding='utf-8') as file:
    text += exclude_imports(file.read(), params["packets"]) + '\n'

build_file_path = params['build']['dir'] + '/' + params['build']['file']
if not os.path.exists(build_file_path):
    with open(build_file_path, 'x') as file:
        file.write('')

with open(build_file_path, 'w', encoding='utf-8') as file:
    file.write(text)