import json
import os
import sys
import glob
import zipfile
import argparse
from subprocess import call

DEFAULT_OPT_FILE = 'optimizer.py'

parser = argparse.ArgumentParser(description='Unzip and find optimizer Python file + create config.json')
parser.add_argument('-i', '--input', help='Input path', required=True)
parser.add_argument('-o', '--output', help='Output path', required=True)
args = vars(parser.parse_args())

# TODO (nit) glob order is arbitrary, so we might want to always sort its output for determinism
for path in glob.glob(os.path.join(args['input'], '*.zip')):
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(args['output'])

default_optimizer_path = os.path.join(args['output'], DEFAULT_OPT_FILE)

# Install any user provided packages
for path in glob.glob(os.path.join(args['output'], '*.whl')):
    status = call(("pip", "install", path), shell=False)
    # TODO some error handling, there might be better way to do this via pip API

optimizer_py = None
if os.path.isfile(default_optimizer_path):
    optimizer_py = DEFAULT_OPT_FILE
else:
    # TODO why is this a for loop here, and we take the last one??
    # Just force participant to name the file optimizer.py (or upload a single py file) to avoid ambiguity??
    for path in glob.glob(os.path.join(args['output'], '*.py')):
        optimizer_py = os.path.basename(path)

if optimizer_py:
    # With this, we will need to remind the user that the constructor in optimizer_py cannot take any kwargs.
    config = {
        "BlackBoxOptimizer": [
            optimizer_py,
            {}
        ]
    }
    with open(os.path.join(args['output'], 'config.json'), 'w') as outfile:
        json.dump(config, outfile)
else:
    sys.exit(os.EX_NOINPUT)
