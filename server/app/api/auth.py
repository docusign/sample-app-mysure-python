import logging
from docusign_esign import ApiException
from flask import Blueprint, jsonify, request, redirect, url_for, session
from flask_cors import cross_origin

from app.ds_client import DsClient
from .utils import process_error
from .session_data import SessionData

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)


@auth.route('/code_grant_auth', methods=['GET'])
@cross_origin()
def code_grant_auth():
    """Handles Code Grant Authorization"""
    try:
        logger.info("Initiating code grant authorization")
        url = DsClient.get_redirect_uri()
        logger.info("Code grant authorization URL generated: %s", url)
    except ApiException as exc:
        logger.error("Error during code grant authorization: %s", str(exc))
        return process_error(exc)

    return jsonify({
        'reason': 'Unauthorized',
        'response': 'Permissions should be granted for current integration',
        'url': url
    }), 401


@auth.route('/callback', methods=['POST'])
@cross_origin()
def callback():
    """Handles OAuth callback"""
    try:
        req_json = request.get_json(force=True)
        logger.info("Received callback request: %s", req_json)
    except TypeError:
        logger.error("Invalid JSON input during callback")
        return jsonify(message='Invalid json input'), 400

    try:
        logger.info("Processing OAuth callback with code: %s", req_json['code'])
        auth_data = DsClient.callback(req_json['code'])
        logger.info("OAuth callback successful, auth data: %s", auth_data)
    except ApiException as exc:
        logger.warning("OAuth callback failed, redirecting to JWT auth: %s", str(exc))
        return redirect(url_for("auth.jwt_auth"), code=307)

    SessionData.set_auth_data(auth_data)
    logger.info("Session data updated successfully after OAuth callback")
    return jsonify(message="Logged in with code grant"), 200


@auth.route('/jwt_auth', methods=['GET'])
@cross_origin()
def jwt_auth():
    """Handles JWT Authentication"""
    try:
        logger.info("Initiating JWT authentication")
        auth_data = DsClient.update_token()
        logger.info("JWT authentication successful, auth data: %s", auth_data)
    except ApiException as exc:
        logger.error("Error during JWT authentication: %s", str(exc))
        return process_error(exc)

    SessionData.set_auth_data(auth_data)
    SessionData.set_payment_data()
    logger.info("Session data and payment data updated successfully after JWT auth")
    return jsonify(message="Logged in with JWT"), 200


@auth.route('/get_status', methods=['GET'])
@cross_origin()
def get_status():
    """Fetches the current authentication status"""
    logged = SessionData.is_logged()
    auth_type = session.get('auth_type')
    logger.info("Auth status checked: logged=%s, auth_type=%s", logged, auth_type)
    return jsonify(logged=logged, auth_type=auth_type), 200


@auth.route('/logout', methods=['POST'])
@cross_origin()
def log_out():
    """Logs the user out and clears the session"""
    logger.info("Logging out user and clearing session data")
    session.clear()
    return jsonify(message="Logged out"), 200


@auth.route('/check_payment', methods=['GET'])
@cross_origin()
def check_payment():
    """Checks if the user has a payment gateway account"""
    try:
        logger.info("Checking user's payment gateway account")
        payment_data = DsClient.check_payment_gateway(session)
        logger.info("Payment gateway check response: %s", payment_data)
    except ApiException as exc:
        logger.error("Error during payment gateway check: %s", str(exc))
        return process_error(exc)

    if payment_data:
        session.update(payment_data)
        logger.info("Payment gateway account found, session updated")
        return jsonify(message="User has a payment gateway account"), 200

    logger.warning("No payment gateway account found for the user")
    return jsonify(message="User doesn't have a payment gateway account"), 402
