#!/usr/bin/env python3
"""
"""
from flask import Flask, jsonify, request, abort, redirect, make_response
from user import Base, User
from auth import Auth

app = Flask(__name__)
AUTH = Auth()


@app.route('/', methods=['GET'])
def message() -> str:
    """return a json payload"""
    msg = {"message": "Bienvenue"}
    return jsonify(msg)


@app.route('/users', methods=['POST'])
def users() -> str:
    """register a user"""
    try:
        email = request.form['email']
        password = request.form['password']
    except KeyError:
        abort(400)

    try:
        user = AUTH.register_user(email, password)
    except ValueError:
        msg = {"message": "email already registered"}
        return jsonify(msg), 400

    msg = {"email": user.email, "message": "user created"}

    return jsonify(msg)


@app.route('/sessions', methods=['DELETE'])
def logout() -> str:
    """logout session"""
    session_id = request.cookies.get('session_id', None)

    if session_id is None:
        abort(403)

    user = AUTH.get_user_from_session_id(session_id)
    if user is None:
        abort(403)

    AUTH.destroy_session(user.id)

    return redirect('/', code=302)


@app.route('/profile', methods=['GET'])
def profile():
    """get user profile"""
    session_id = request.cookies.get('session_id', None)
    if session_id is None:
        abort(403)
    user = AUTH.get_user_from_session_id(session_id)
    if user is None:
        abort(403)

    return jsonify({"email": user.email}), 200


@app.route('/reset_password', methods=['POST'])
def get_reset_password_token():
    """Get reset password token"""
    try:
        email = request.form['email']
    except KeyError:
        abort(403)

    token: str = ''
    try:
        token = AUTH.get_reset_password_token(email)
    except ValueError:
        abort(403)

    msg = {"email": email, "reset_token": token}

    return jsonify(msg), 200


@app.route('/reset_password', methods=['PUT'])
def update_password():
    """Update password"""
    try:
        email = request.form['email']
        reset_token = request.form['reset_token']
        new_password = request.form['new_password']
    except KeyError:
        abort(403)

    try:
        AUTH.update_password(reset_token, new_password)
    except ValueError:
        abort(403)
    msg = {"email": email, "message": "Password updated"}
    return jsonify(msg), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
