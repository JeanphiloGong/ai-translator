#!/bin/bash
# Activate the virtual environment
source "/www/创业项目/ai-translator/tl/bin/activate"

# Run the translator script with the -c Option
python3 "/www/创业项目/ai-translator/translator.py" "$@"

