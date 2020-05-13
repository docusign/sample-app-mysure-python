import base64
from os import path

from jinja2 import BaseLoader, Environment

from app.const import TPL_PATH, CLICKWRAP_BASE_HOST, CLICKWRAP_BASE_URI
from app.ds_client import DsClient


class Clickwrap:
    @classmethod
    def create(cls, args):
        """Creates a clickwrap for an account
        Parameters:
            args (dict): Parameters for the clickwrap.
        Returns:
            JSON structure of the created clickwrap.
        """
        display_name = args.get('display_name')
        terms_name = args.get('terms_name')
        terms_renewal = args.get('terms_renewal')

        with open(path.join(TPL_PATH, 'terms-renewal.html'), 'r') as file:
            terms = file.read()
        terms = Environment(loader=BaseLoader).from_string(terms).render(
            terms_renewal=terms_renewal,
        )
        base64_terms = base64.b64encode(bytes(terms, 'utf-8')).decode('ascii')

        # Construct clickwrap JSON body
        body = {
            'displaySettings': {
                'consentButtonText': 'I Agree',
                'displayName': display_name,
                'downloadable': True,
                'format': 'modal',
                'hasAccept': True,
                'mustRead': True,
                'mustView': True,
                'requireAccept': True,
                'size': 'medium',
                'documentDisplay': 'document',
            },
            'documents': [
                {
                    'documentHtml': terms,
                    'documentName': terms_name,
                    'order': 1
                }
            ],
            'name': terms_name,
            'requireReacceptance': True
        }

        # Make a POST call to the clickwraps endpoint to create a clickwrap for an account
        ds_client = DsClient.get_instance(CLICKWRAP_BASE_HOST)
        uri = f"{CLICKWRAP_BASE_URI}/{ds_client.account_id}/clickwraps"
        response = ds_client.api_client.call_api(
            uri, 'POST', body=body, response_type='object'
        )
        clickwrap_id = response[0].get('clickwrapId')

        # Make a PUT call to the clickwraps endpoint to activate created clickwrap
        uri = f"{CLICKWRAP_BASE_URI}/{ds_client.account_id}/clickwraps/{clickwrap_id}/versions/1"
        response_active = ds_client.api_client.call_api(
            uri, 'PUT', body={'status': 'active'}, response_type='object'
        )
        return response_active[0]