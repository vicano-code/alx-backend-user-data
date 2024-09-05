#!/usr/bin/env python3
""" Module of Users views
"""
from api.v1.views import app_views
from flask import abort, jsonify, request, make_response
from models.user import User
from os import getenv


@app_views.route('/auth_session/login', methods=['POST'], strict_slashes=False)
def login():
    """Auth session Login
      Return session with credentials
    """
    email = request.form.get('email')
    if not email:
        return make_response(jsonify({"error": "email missing"}), 400)

    passwd = request.form.get('password')
    if not passwd:
        return make_response(jsonify({"error": "password missing"}), 400)

    user_search = User.search({'email': email})
    if len(user_search) == 0:
        error_msg = {"error": "no user found for this email"}
        return make_response(jsonify(error_msg), 400)

    from api.v1.app import auth
    for user in user_search:
        if (user.is_valid_password(passwd)):
            session_id = auth.create_session(user.id)
            session_name = getenv('SESSION_NAME')
            response = make_response(user.to_json())
            response.set_cookie(session_name, session_id)
            return response

    return make_response(jsonify({"error": "wrong password"}), 401)


@app_views.route('/auth_session/logout',
                 methods=['DELETE'], strict_slashes=False)
def logout():
    """logout from session"""
    from api.v1.app import auth

    end_session = auth.destroy_session(request)
    if end_session is False:
        abort(404)

    return jsonify({}), 200
