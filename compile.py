import json
import os.path, os

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
    with open(filename, 'r', encoding='utf-8') as file:
        text += file.read() + '\n\n'

text += """##############################################################
# """ + params["main"] + """ (MAIN) file content:
"""
with open(params["main"], 'r', encoding='utf-8') as file:
    text += file.read() + '\n'

build_file_path = params['build']['dir'] + '/' + params['build']['file']
if not os.path.exists(build_file_path):
    with open(build_file_path, 'x') as file:
        file.write('')

with open(build_file_path, 'w', encoding='utf-8') as file:
    file.write(text)