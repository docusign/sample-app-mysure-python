@echo off

cd ..

python -m venv venv

call ./venv/Scripts/activate

pip install --upgrade pip
pip install -r requirements.txt

npm install --no-optional

cd scripts
