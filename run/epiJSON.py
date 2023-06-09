#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# settings
image = "bigdatainbiomedicine/needl:latest"
command = '/NeEDL/test/model/bin/epiJSON'

# app arguments
arguments = sys.argv[1:]

print(arguments)

# map output path
output_directory = None
for i, arg in enumerate(arguments):
    if arg == '--output-directory':
        if len(arguments) > i + 1:
            output_directory = os.path.abspath(arguments[i + 1])
            if not os.path.exists(output_directory):
                print(f'Error: output directory {output_directory} does not exist!')
                exit(-1)

            arguments[i + 1] = '/mnt/out/'

        break

# map all input files and directories
input_paths = []

# normal paths
normal_path_attribs = ['--input-file', '--disease-snps']
for i, arg in enumerate(arguments):
    if arg in normal_path_attribs:
        if len(arguments) > i + 1:
            # can be multiple files (plink) so always mount the whole directory
            path = os.path.abspath(arguments[i + 1])
            filename = ""
            if not os.path.isdir(path):
                filename = os.path.basename(path)
                path = str(Path(path).parent.resolve())
            if not os.path.exists(path):
                print(f'Error: path {path} at argument {arg} does not exist!')
                exit(-1)

            arguments[i + 1] = '/mnt/in_' + str(len(input_paths)) + '/' + filename
            input_paths.append(path)


# --ext-directory
if '--ext-directory' in arguments:
    print("Error: It is not allowed to set the argument --ext-directory when using NeEDL in docker mode. All necessary files within the ext directory are already at the correct place in the docker container.")
    exit(1)

# --data-directory
if '--data-directory' in arguments:
    print("Error: It is not allowed to set the argument --data-directory when using NeEDL in docker mode. All necessary files within the data directory are already at the correct place in the docker container.")
    exit(1)

volume_string = ' '.join([f'-v "{file}:/mnt/in_{i}:rw,Z"' for i, file in enumerate(input_paths)])

external_command = f"docker run --user='{os.getuid()}':'{os.getgid()}' {volume_string}"

if output_directory is not None:
    external_command += f' -v "{output_directory}:/mnt/out:rw,Z" '

argument_string = ' '.join(map(lambda a: f'"{a}"', map(lambda b: b.replace('"', '\\"'), arguments)))

external_command += f"{image} {command} --ext-directory /NeEDL/ext/ --data-directory /NeEDL/data/ {argument_string}"

print(external_command)

os.system("docker image pull " + image)
os.system(external_command)
