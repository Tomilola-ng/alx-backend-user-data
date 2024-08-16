#!/usr/bin/env python3

""" Flask API Routes for Authentication Service """
# pylint: disable=raise-missing-from

from auth import Auth
from flask import (Flask, request, jsonify,
                   abort, redirect)

app = Flask(__name__)

AUTH = Auth()


@app.route('/', methods=['GET'])
def hello_world() -> str:
    """
        Endpoint for authentication service API
        Returns a JSON Payload with a message
    """
    response = {"message": "Bienvenue"}
    return jsonify(response)


@app.route('/users', methods=['POST'])
def register_user() -> str:
    """
        Endpoint for registering a new user
        Returns a JSON Payload with a message
        or Aborts with a 400 HTTP status
    """
    try:
        p_email = request.form['email']
        p_password = request.form['password']
    except KeyError:
        abort(400)

    try:
        AUTH.register_user(p_email, p_password)
    except ValueError:
        return jsonify({"message": "email already registered"}), 400

    response = {"email": p_email, "message": "user created"}
    return jsonify(response)


@app.route('/sessions', methods=['POST'])
def log_in() -> str:
    """
        Endpoint for logging in a user
        Returns a JSON Payload with a message
        or Aborts with a 401 HTTP status
    """
    try:
        p_email = request.form['email']
        p_password = request.form['password']
    except KeyError:
        abort(400)

    if not AUTH.valid_login(p_email, p_password):
        abort(401)

    session_id = AUTH.create_session(p_email)

    response = {"email": p_email, "message": "logged in"}
    response = jsonify(response)

    response.set_cookie("session_id", session_id)

    return response


@app.route('/sessions', methods=['DELETE'])
def log_out() -> str:
    """
        Endpoint for logging out a user
        Returns Redirect to GET /
    """
    session_id = request.cookies.get("session_id", None)

    if session_id is None:
        abort(403)

    user_obj = AUTH.get_user_from_session_id(session_id)

    if user_obj is None:
        abort(403)

    AUTH.destroy_session(user_obj.id)

    return redirect('/')


@app.route('/profile', methods=['GET'])
def profile() -> str:
    """
        Endpoint for getting a user's profile
        Returns a JSON Payload with a message
        With a 200 HTTP status
        Or Aborts with a 403 HTTP status
    """
    session_id = request.cookies.get("session_id", None)

    if session_id is None:
        abort(403)

    user_obj = AUTH.get_user_from_session_id(session_id)

    if user_obj is None:
        abort(403)

    response = {"email": user_obj.email}

    return jsonify(response), 200


@app.route('/reset_password', methods=['POST'])
def reset_password() -> str:
    """
        Endpoint for resetting a user's password
        Returns a JSON Payload with a message
        With a 200 HTTP status
        or Aborts with a 403 HTTP status
    """
    try:
        p_email = request.form['email']
    except KeyError:
        abort(403)

    try:
        reset_token = AUTH.get_reset_password_token(p_email)
    except ValueError:
        abort(403)

    response = {"email": p_email, "reset_token": reset_token}

    return jsonify(response), 200


@app.route('/reset_password', methods=['PUT'])
def update_password() -> str:
    """
        Endpoint for updating a user's password
        Returns a JSON Payload with a message
        With a 200 HTTP status
        or Aborts with a 403 HTTP status
    """
    try:
        email = request.form['email']
        reset_token = request.form['reset_token']
        new_password = request.form['new_password']
    except KeyError:
        abort(400)

    try:
        AUTH.update_password(reset_token, new_password)
    except ValueError:
        abort(403)

    response = {"email": email, "message": "Password updated"}
    return jsonify(response), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
