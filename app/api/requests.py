from docusign_esign import ApiException
from flask import Blueprint, jsonify, request, session
from flask_cors import cross_origin

from app.api.utils import process_error, check_token
from app.document import DsDocument
from app.ds_config import DsConfig
from app.envelope import Envelope

requests = Blueprint('requests', __name__)


@requests.route('/requests/claim', methods=['POST'])
@cross_origin(supports_credentials=True)
@check_token
def submit_claim():
    """Submit a claim"""
    try:
        req_json = request.get_json(force=True)
        claim = req_json['claim']
        envelope_args = {
            'signer_client_id': 1000,
            'ds_return_url': req_json['callback-url'],
        }
    except TypeError:
        return jsonify(message='Invalid JSON input'), 400

    try:
        # Create envelope
        envelope = DsDocument.create_claim('submit-claim.html', claim, envelope_args)
        # Submit envelope to the Docusign
        envelope_id = Envelope.send(envelope)
        user_documents = session.get('ds_documents')
        if not user_documents:
            session['ds_documents'] = [envelope_id]
        else:
            user_documents.append(envelope_id)
            session['ds_documents'] = user_documents

        # Get the recipient view
        result = Envelope.get_view(envelope_id, envelope_args, claim)
    except ApiException as ex:
        return process_error(ex)
    return jsonify({'envelope_id': envelope_id, 'redirect_url': result.url})


@requests.route('/requests/newinsurance', methods=['POST'])
@cross_origin(supports_credentials=True)
@check_token
def buy_new_insurance():
    """Request for the purchase of a new insurance"""
    try:
        req_json = request.get_json(force=True)
        insurance_info = req_json['insurance']
        user = req_json['user']

        envelope_args = {
            'signer_client_id': 1000,
            'ds_return_url': req_json['callback-url'],
            'gateway_account_id': DsConfig.gateway_id(),
            'gateway_name': DsConfig.gateway_name(),
            'gateway_display_name': DsConfig.gateway_display_name()
        }
    except TypeError:
        return jsonify(message='Invalid JSON input'), 400

    try:
        # Create envelope with payment
        envelope = DsDocument.create_with_payment(
            'new-insurance.html', user, insurance_info, envelope_args
        )
        # Submit envelope to the Docusign
        envelope_id = Envelope.send(envelope)
        user_documents = session.get('ds_documents')
        if not user_documents:
            session['ds_documents'] = [envelope_id]
        else:
            user_documents.append(envelope_id)
            session['ds_documents'] = user_documents
        # Get the recipient view
        result = Envelope.get_view(envelope_id, envelope_args, user)
    except ApiException as ex:
        return process_error(ex)
    return jsonify({'envelope_id': envelope_id, 'redirect_url': result.url})


@requests.route('/requests', methods=['GET'])
@cross_origin(supports_credentials=True)
def envelope_list():
    """Request for envelope list"""
    try:
        envelope_args = {
            'from_date': request.args.get('from-date')
        }
    except TypeError:
        return jsonify(message='Invalid JSON input'), 400

    try:
        user_documents = session.get('ds_documents')
        if not user_documents:
            user_documents = []
        envelopes = Envelope.list(envelope_args, user_documents)
    except ApiException as ex:
        return process_error(ex)
    return jsonify({'envelopes': envelopes})


@requests.route('/requests/download', methods=['GET'])
@cross_origin(supports_credentials=True)
@check_token
def envelope_download():
    """Request for document download from the envelope"""
    try:
        envelope_args = {
            'envelope_id': request.args['envelope-id'],
            "document_id": request.args['document-id'],
        }
    except TypeError:
        return jsonify(message="Invalid JSON input"), 400
    try:
        envelope_file = Envelope.download(envelope_args)
    except ApiException as e:
        return process_error(e)
    return envelope_file
