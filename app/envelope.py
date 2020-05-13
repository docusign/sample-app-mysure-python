import os

from docusign_esign import EnvelopesApi, RecipientViewRequest
from flask import send_from_directory

from app.ds_client import DsClient


class Envelope:
    @classmethod
    def send(cls, envelope):
        """Send an envelope
        Parameters:
            envelope (object): EnvelopeDefinition object
        Returns:
            envelope_id (str): envelope ID
        """
        # Call Envelopes create API method
        # Exceptions will be caught by the calling function
        ds_client = DsClient.get_instance()
        envelope_api = EnvelopesApi(ds_client.api_client)
        results = envelope_api.create_envelope(
            ds_client.account_id,
            envelope_definition=envelope
        )
        return results.envelope_id

    @classmethod
    def get_view(cls, envelope_id, envelope_args, user, authentication_method='None'):
        """Get the recipient view
        Parameters:
            envelope_id (str): Envelope ID
            envelope_args (dict): Parameters of the document
            user (dict): User information
            authentication_method (str): Authentication method
        Returns:
            URL to the recipient view UI
        """
        # Create the recipient view request object
        recipient_view_request = RecipientViewRequest(
            authentication_method=authentication_method,
            client_user_id=envelope_args['signer_client_id'],
            recipient_id='1',
            return_url=envelope_args['ds_return_url'],
            user_name=f"{user['first_name']} {user['last_name']}",
            email=user['email']
        )
        # Obtain the recipient view URL for the signing ceremony
        # Exceptions will be caught by the calling function
        ds_client = DsClient.get_instance()
        envelope_api = EnvelopesApi(ds_client.api_client)
        results = envelope_api.create_recipient_view(
            ds_client.account_id,
            envelope_id,
            recipient_view_request=recipient_view_request
        )
        return results

    @classmethod
    def list(cls, envelope_args, user_documents):
        """Get status changes for one or more envelopes
        Parameters:
            envelope_args (dict): Document parameters
            user_documents (list): Documents signed by user
        Returns:
            EnvelopesInformation
        """
        ds_client = DsClient.get_instance()
        envelope_api = EnvelopesApi(ds_client.api_client)
        envelopes_info = envelope_api.list_status_changes(
            ds_client.account_id,
            from_date=envelope_args['from_date'],
            include='recipients'
        )
        if not envelopes_info.envelopes:
            return []
        results = [env.to_dict() for env in envelopes_info.envelopes
                   if env.envelope_id in user_documents]
        return results

    @classmethod
    def download(cls, args):
        """Download the specified document from the envelope"""
        ds_client = DsClient.get_instance()
        envelope_api = EnvelopesApi(ds_client.api_client)
        file_path = envelope_api.get_document(
            ds_client.account_id, args['document_id'], args['envelope_id']
        )
        (dirname, filename) = os.path.split(file_path)
        return send_from_directory(
            directory=dirname,
            filename=filename,
            as_attachment=True
        )