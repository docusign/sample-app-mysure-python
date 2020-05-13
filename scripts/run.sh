#!/bin/bash
cd ..
# Activate virtual environment
source venv/bin/activate
# Run front end
npm start > /dev/null 2>&1 &
# Run back end
flask run --host 0.0.0.0 --port 5001 > /dev/null 2>&1 &
cd scripts