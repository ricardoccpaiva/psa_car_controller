"""
PSA OTP REST API

A simple REST API to manage PSA OTP (One-Time Password) flows.

Endpoints:
    POST /otp/setup - Setup OTP session with SMS code and PIN
    POST /otp/generate - Generate OTP code from session
    GET /otp/status - Check if OTP session exists
    DELETE /otp/session - Delete OTP session

Author: Extracted from PSA Car Controller
Version: 1.0.0
"""

from flask import Flask, request, jsonify
import os
import sys
from pathlib import Path

# Add OTP module to path
OTP_MODULE_PATH = Path(__file__).parent / "otp_module"
sys.path.insert(0, str(OTP_MODULE_PATH))

try:
    from otp import new_otp_session, load_otp, save_otp, ConfigException
except ImportError as e:
    print(f"ERROR: Failed to import OTP module: {e}")
    print(f"Make sure OTP files are in: {OTP_MODULE_PATH}")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)

# Configuration
SESSION_FILE = os.environ.get("OTP_SESSION_FILE", "otp.bin")
HOST = os.environ.get("API_HOST", "0.0.0.0")
PORT = int(os.environ.get("API_PORT", "5000"))
DEBUG = os.environ.get("API_DEBUG", "false").lower() == "true"


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "PSA OTP API",
        "version": "1.0.0"
    }), 200


@app.route("/otp/setup", methods=["POST"])
def otp_setup():
    """
    Setup OTP session with SMS code and PIN

    Request Body (JSON):
        {
            "sms_code": "123456",
            "pin_code": "1234"
        }

    Response:
        Success (200):
        {
            "status": "success",
            "device_id": "a1b2c3d4e5f6g7h8",
            "session_file": "otp.bin"
        }

        Error (400/500):
        {
            "status": "error",
            "error": "Error message"
        }
    """
    try:
        # Parse request
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "error": "Request body must be JSON"
            }), 400

        sms_code = data.get("sms_code")
        pin_code = data.get("pin_code")

        # Validate inputs
        if not sms_code:
            return jsonify({
                "status": "error",
                "error": "sms_code is required"
            }), 400

        if not pin_code:
            return jsonify({
                "status": "error",
                "error": "pin_code is required"
            }), 400

        if not str(pin_code).isdigit():
            return jsonify({
                "status": "error",
                "error": "pin_code must be numeric"
            }), 400

        # Create OTP session
        otp_session = new_otp_session(str(sms_code), str(pin_code))

        if otp_session is None:
            return jsonify({
                "status": "error",
                "error": "Failed to create OTP session"
            }), 500

        # Save session
        save_otp(otp_session, SESSION_FILE)

        return jsonify({
            "status": "success",
            "device_id": otp_session.device_id,
            "session_file": SESSION_FILE
        }), 200

    except ConfigException as e:
        return jsonify({
            "status": "error",
            "error": f"Configuration error: {str(e)}"
        }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route("/otp/generate", methods=["POST"])
def otp_generate():
    """
    Generate OTP code from existing session

    Request Body (JSON - optional):
        {
            "session_file": "otp.bin"  # Optional, defaults to configured file
        }

    Response:
        Success (200):
        {
            "status": "success",
            "otp_code": "a3k9m2"
        }

        Error (400/404/500):
        {
            "status": "error",
            "error": "Error message"
        }
    """
    try:
        # Parse request (optional session file)
        data = request.get_json() or {}
        session_file = data.get("session_file", SESSION_FILE)

        # Check if session file exists
        if not os.path.exists(session_file):
            return jsonify({
                "status": "error",
                "error": f"Session file not found: {session_file}. Run /otp/setup first."
            }), 404

        # Load OTP session
        otp_session = load_otp(session_file)

        if otp_session is None:
            return jsonify({
                "status": "error",
                "error": "Failed to load OTP session. File may be corrupted."
            }), 500

        # Generate OTP code
        otp_code = otp_session.get_otp_code()

        if otp_code is None:
            return jsonify({
                "status": "error",
                "error": "Failed to generate OTP code"
            }), 500

        # Save updated session (counter incremented)
        save_otp(otp_session, session_file)

        return jsonify({
            "status": "success",
            "otp_code": otp_code
        }), 200

    except ConfigException as e:
        return jsonify({
            "status": "error",
            "error": f"Configuration error: {str(e)}. Session may have expired."
        }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route("/otp/status", methods=["GET"])
def otp_status():
    """
    Check if OTP session exists

    Query Parameters:
        session_file (optional): Custom session file path

    Response:
        {
            "status": "success",
            "session_exists": true,
            "session_file": "otp.bin"
        }
    """
    try:
        session_file = request.args.get("session_file", SESSION_FILE)
        session_exists = os.path.exists(session_file)

        return jsonify({
            "status": "success",
            "session_exists": session_exists,
            "session_file": session_file
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route("/otp/session", methods=["DELETE"])
def delete_session():
    """
    Delete OTP session file

    Request Body (JSON - optional):
        {
            "session_file": "otp.bin"  # Optional, defaults to configured file
        }

    Response:
        Success (200):
        {
            "status": "success",
            "message": "Session deleted"
        }

        Error (404/500):
        {
            "status": "error",
            "error": "Error message"
        }
    """
    try:
        data = request.get_json() or {}
        session_file = data.get("session_file", SESSION_FILE)

        if not os.path.exists(session_file):
            return jsonify({
                "status": "error",
                "error": f"Session file not found: {session_file}"
            }), 404

        os.remove(session_file)

        return jsonify({
            "status": "success",
            "message": "Session deleted"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "status": "error",
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        "status": "error",
        "error": "Method not allowed"
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "status": "error",
        "error": "Internal server error"
    }), 500


if __name__ == "__main__":
    print("=" * 70)
    print("PSA OTP REST API")
    print("=" * 70)
    print(f"Host: {HOST}")
    print(f"Port: {PORT}")
    print(f"Debug: {DEBUG}")
    print(f"Session File: {SESSION_FILE}")
    print("=" * 70)
    print()
    print("Endpoints:")
    print("  POST   /otp/setup     - Setup OTP session")
    print("  POST   /otp/generate  - Generate OTP code")
    print("  GET    /otp/status    - Check session status")
    print("  DELETE /otp/session   - Delete session")
    print("  GET    /health        - Health check")
    print()
    print("Starting server...")
    print("=" * 70)
    print()

    app.run(host=HOST, port=PORT, debug=DEBUG)
