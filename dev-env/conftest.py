import sys
import os

# Adjust the path so Python can find the 'common' package.
# This assumes your conftest.py is in the dev-env directory.
layer_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "./common_layer/python"))
if layer_path not in sys.path:
    sys.path.insert(0, layer_path)