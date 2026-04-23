@echo off

cd ..

python -m venv venv

call ./venv/Scripts/activate

cd server
pip install --upgrade pip
pip install -r requirements.txt

cd ../client
npm install --no-optional

cd ../scripts
