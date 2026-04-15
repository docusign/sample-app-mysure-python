import os
from docusign_esign import ApiException
from flask import Blueprint, jsonify, request, session
from flask_cors import cross_origin

from app.api.utils import process_error, check_token
from app.document import DsDocument
from app.envelope import Envelope
from app.envelope_status_store import envelope_status_store
from app.socket import publish_envelope_status

from .session_data import SessionData
from app.ds_config import CONNECTED_FIELDS_BASE_HOST
import json
import datetime


requests = Blueprint('requests', __name__)


def _extract_event_data(payload):
    """Extract event data from the payload."""
    event = payload.get('event', '')
    return _extract_extension_event_data(payload) if event.startswith('extension-') else _extract_envelope_event_data(payload)


def _extract_envelope_event_data(payload):
    event = payload.get('event', '')

    data = payload.get('data', {}) if isinstance(payload, dict) else {}
    envelope_id = data.get('envelopeId', '')
    envelope_summary = data.get('envelopeSummary', {}) if isinstance(data, dict) else {}
    subject = envelope_summary.get('emailSubject', '')
    status = envelope_summary.get('status', '')
    status_timestamp = envelope_summary.get('statusChangedDateTime', '')

    recipients = envelope_summary.get('recipients', {})
    signers = recipients.get('signers', []) if isinstance(recipients, dict) else []
    signer_name = signers[0].get('name', '') if len(signers) > 0 else ''

    return {
        'event': event,
        'envelope_id': envelope_id,
        'subject': subject,
        'status': status,
        'status_timestamp': status_timestamp,
        'signer_name': signer_name,
    }

def _extract_extension_event_data(payload):
    event = payload.get('event', '')

    data = payload.get('data', {}) if isinstance(payload, dict) else {}
    envelope_id = data.get('entityId', '')
    extension = data.get('extension', {}) if isinstance(data, dict) else {}
    actionContract = extension.get('actionContract', '')
    appName = extension.get('appName', '')
    attempt_time = extension.get('attemptTime', '')

    verification_data = extension.get('data', {})
    verified = verification_data.get('verified', False) if isinstance(verification_data, dict) else False

    return {
        'event': event,
        'envelope_id': envelope_id,
        'actionContract': actionContract,
        'appName': appName,
        'attempt_time': attempt_time,
        'verified': verified,
    }

@requests.route('/extensionApps', methods=['GET'])
@cross_origin()
def extension_apps():
    """Request for extension apps"""

    access_token = session.get('access_token')
    account_id = session.get('account_id')

    try:
        extensions = Extensions.getExtensions(account_id, access_token, CONNECTED_FIELDS_BASE_HOST)

        session['extensions'] = json.dumps(extensions)
        actual_app_ids = [item["appId"] for item in extensions]

        address_extension_id = Extensions.getAddressExtensionId()
        email_extension_ids = Extensions.getEmailExtensionIds()

        has_required_app = address_extension_id in actual_app_ids
        has_at_least_one_optional = any(app_id in actual_app_ids for app_id in email_extension_ids)

        has_all_app_ids = has_required_app and has_at_least_one_optional
    except ApiException as exc:
        return process_error(exc)
    return jsonify({'areExtensionsPresent': has_all_app_ids})


@requests.route('/requests/claim', methods=['POST'])
@cross_origin()
@check_token
def submit_claim():
    """Submit a claim"""
    try:
        req_json = request.get_json(force=True)
    except TypeError:
        return jsonify(message='Invalid JSON input'), 400

    claim = req_json['claim']
    envelope_args = {
        'signer_client_id': 1000,
        'ds_return_url': req_json['callback-url'],
        'monitor_callback_url': os.environ.get('MONITOR_CALLBACK_URL'),
    }

    try:
        # Create envelope
        envelope = DsDocument.create_claim('submit-claim.html', claim, envelope_args)
        # Submit envelope to the Docusign
        envelope_id = Envelope.send(envelope, session)

        data = {
            'event': 'envelope-sent',
            'envelope_id': envelope_id,
            'subject': envelope.email_subject,
            'status': 'sent',
            'status_timestamp': datetime.datetime.now().isoformat(),
            'signer_name': f"{claim['first_name']} {claim['last_name']}",
        }
        envelope_status_store.upsert(data)
        publish_envelope_status()
    except ApiException as exc:
        return process_error(exc)

    SessionData.set_ds_documents(envelope_id)

    try:
        # Get the recipient view
        result = Envelope.get_view(envelope_id, envelope_args, claim, session)
    except ApiException as exc:
        return process_error(exc)
    return jsonify({'envelope_id': envelope_id, 'redirect_url': result.url})


@requests.route('/requests/newinsurance', methods=['POST'])
@cross_origin()
@check_token
def buy_new_insurance():
    """Request for the purchase of a new insurance"""
    try:
        req_json = request.get_json(force=True)
    except TypeError:
        return jsonify(message='Invalid JSON input'), 400

    insurance_info = req_json['insurance']
    user = req_json['user']

    envelope_args = {
        'signer_client_id': 1000,
        'ds_return_url': req_json['callback-url'],
        'gateway_account_id': os.environ.get('DS_PAYMENT_GATEWAY_ID'),
        'gateway_name': os.environ.get('DS_PAYMENT_GATEWAY_NAME'),
        'payment_display_name': os.environ.get('DS_PAYMENT_GATEWAY_DISPLAY_NAME'),
    }

    try:
        # Create envelope with payment
        envelope = DsDocument.create_with_payment(
            'new-insurance.html', user, insurance_info, envelope_args
        )
        # Submit envelope to the Docusign
        envelope_id = Envelope.send(envelope, session)

        data = {
            'event': 'envelope-sent',
            'envelope_id': envelope_id,
            'subject': envelope.email_subject,
            'status': 'sent',
            'status_timestamp': '',
            'signer_name': f"{user['first_name']} {user['last_name']}",
        }
        envelope_status_store.upsert(data)
        publish_envelope_status()
    except ApiException as exc:
        return process_error(exc)

    SessionData.set_ds_documents(envelope_id)

    try:
        # Get the recipient view
        result = Envelope.get_view(envelope_id, envelope_args, user, session)
    except ApiException as exc:
        return process_error(exc)
    return jsonify({'envelope_id': envelope_id, 'redirect_url': result.url})


@requests.route('/requests', methods=['GET'])
@cross_origin()
def envelope_list():
    """Request for envelope list"""
    try:
        envelope_args = {
            'from_date': request.args.get('from-date')
        }
    except TypeError:
        return jsonify(message='Invalid JSON input'), 400

    user_documents = session.get('ds_documents', [])

    try:
        envelopes = Envelope.list(envelope_args, user_documents, session)
    except ApiException as exc:
        return process_error(exc)
    return jsonify({'envelopes': envelopes})


@requests.route('/requests/download', methods=['GET'])
@cross_origin()
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
        envelope_file = Envelope.download(envelope_args, session)
    except ApiException as exc:
        return process_error(exc)
    return envelope_file


@requests.route('/monitor/envelopes/status', methods=['POST'])
@cross_origin()
def monitor_envelope_status():
    """Receive Docusign monitor updates."""
    payload = request.get_json(silent=True)
    if not payload or not isinstance(payload, dict):
        return jsonify(message='Invalid JSON input'), 400

    data = _extract_event_data(payload)

    envelope_status_store.upsert(data)
    publish_envelope_status()
    
    return jsonify(data), 200
