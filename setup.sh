#!bin/bash
os=$(uname)
arch=$(uname -m)
conda_dir="$HOME/miniconda3"

source $conda_dir/bin/activate
if ! command -- "conda" > /dev/null 2>&1; then
    if [ "$os" == "Linux" ]; then
        sudo apt update
        sudo apt install curl
    elif [ "$os" == "Darwin" ]; then
        os="MacOSX"
    fi

    mkdir -p $conda_dir
    curl https://repo.anaconda.com/miniconda/Miniconda3-latest-"$os"-"$arch".sh -o $conda_dir/miniconda.sh
    bash $conda_dir/miniconda.sh -b -u -p $conda_dir
    rm $conda_dir/miniconda.sh
fi

source $conda_dir/bin/activate
if ! conda env list | grep -q "^yolo_env\b"; then
    conda create -n yolo_env python=3.12 -y
fi
source $conda_dir/bin/activate yolo_env
if [ $? -eq 0 ]; then
    pip install -r requirements.txt
fi
