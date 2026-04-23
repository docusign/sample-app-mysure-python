from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from flask_session import Session

from app.api import clickwrap, requests, common, auth
from app.socket import init_realtime

load_dotenv()

URL_PREFIX = '/api'

app = Flask(__name__)
app.config.from_pyfile("config.py")

# Add server-side session config
app.config.update(
    SESSION_TYPE="filesystem",             
    SESSION_FILE_DIR="/tmp/flask_session",
    SESSION_PERMANENT=False,
    SESSION_USE_SIGNER=True,
    SESSION_COOKIE_NAME="sid"        
)

Session(app) 

app.register_blueprint(clickwrap, url_prefix=URL_PREFIX)
app.register_blueprint(common, url_prefix=URL_PREFIX)
app.register_blueprint(requests, url_prefix=URL_PREFIX)
app.register_blueprint(auth, url_prefix=URL_PREFIX)

init_realtime(app)

cors = CORS(app)
