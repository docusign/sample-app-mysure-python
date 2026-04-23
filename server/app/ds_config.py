import os

TPL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates/')
)
IMG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "images/")
)

TOKEN_EXPIRATION_IN_SECONDS = 3600
TOKEN_REPLACEMENT_IN_SECONDS = 10 * 60

CLICKWRAP_BASE_HOST = 'https://demo.docusign.net'
CLICKWRAP_BASE_URI = '/clickapi/v1/accounts'
CLICKWRAP_TIME_DELTA_IN_MINUTES = 15

CONNECTED_FIELDS_BASE_HOST = 'https://api-d.docusign.com'
TWILIO_EXTENSION_ID = "6ff9ae39-ad45-4d04-b0c2-a6e2214f5925"
EMAILABLE_EXTENSION_ID = "5e3b623f-afaf-45da-b6a0-f5abc3c32128"
SMARTY_EXTENSION_ID = "04bfc1ae-1ba0-42d0-8c02-264417a7b234"

CODE_GRANT_SCOPES =  ['signature', 'impersonation', 'click.manage', 'adm_store_unified_repo_read']
PERMISSION_SCOPES = ['signature', 'impersonation', 'click.manage', 'adm_store_unified_repo_read']

DS_RETURN_URL = os.environ.get('REACT_APP_DS_RETURN_URL')
DS_AUTH_SERVER = os.environ.get('DS_AUTH_SERVER')
DS_DEMO_SERVER = os.environ.get('REACT_APP_DS_DEMO_SERVER')
