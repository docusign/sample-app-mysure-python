#!/bin/bash
# Backend installation
# Create virtual environment for the project

# echo "Move installation to Docker file"

cd ..

python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install required python packages
cd server
pip3 install --upgrade pip3
pip3 install -r requirements.txt

# Frontend installation
cd ../client
npm install --no-optional

cd ../scripts || exit
