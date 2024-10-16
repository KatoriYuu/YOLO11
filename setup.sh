#!bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
python3 -m venv "$SCRIPT_DIR/yolo_env"
source "$SCRIPT_DIR/yolo_env/bin/activate"
pip3 install -r "$SCRIPT_DIR/requirements.txt"
