#!/usr/bin/env python3
"""Module Basic Auth
"""
from api.v1.auth.auth import Auth
from base64 import b64decode, binascii
from models.user import User
from typing import TypeVar, List


class BasicAuth(Auth):
    """Basic Auth class
    """
    def __init__(self):
        """Constructor"""

    def extract_base64_authorization_header(self, authorization_header: str
                                            ) -> str:
        """Extract authorization_header in base 64
        """
        if authorization_header is None or type(authorization_header) != str:
            return None
        if not authorization_header.startswith("Basic ")\
           and not authorization_header.endswith(" "):
            return None

        return authorization_header.split()[1]

    def decode_base64_authorization_header(
                                           self,
                                           base64_authorization_header: str
                                           ) -> str:
        """decode base64 authorization header
        """
        if base64_authorization_header is None\
           or type(base64_authorization_header) != str:
            return None
        try:
            decoded_data = b64decode(base64_authorization_header)
        except binascii.Error as er:
            return None

        return decoded_data.decode('utf-8')

    def extract_user_credentials(self, decoded_base64_authorization_header: str
                                 ) -> (str, str):
        """returns the user email and password from the Base64 decoded value
        """
        if decoded_base64_authorization_header is None\
           or type(decoded_base64_authorization_header) != str\
           or ':' not in decoded_base64_authorization_header:
            return None, None

        user_credentials = decoded_base64_authorization_header.split(':', 1)
        return user_credentials[0], user_credentials[1]

    def user_object_from_credentials(self, user_email: str, user_pwd: str
                                     ) -> TypeVar('User'):
        """returns the User instance given the email and password
        """
        if user_email is None or type(user_email) != str:
            return None
        if user_pwd is None or type(user_pwd) != str:
            return None
        try:
            exist_user: List[TypeVar('User')]
            exist_user = User.search({"email": user_email})
        except Exception:
            return None

        for user in exist_user:
            if user.is_valid_password(user_pwd):
                return user
        return None

    def current_user(self, request=None) -> TypeVar('User'):
        """overloads Auth and retrieves the User instance for a request
        """
        header: str = self.authorization_header(request)

        if header is None:
            return None

        auth_head: str = self.extract_base64_authorization_header(header)
        if auth_head is None:
            return None

        decode_auth: str = self.decode_base64_authorization_header(auth_head)
        if decode_auth is None:
            return decode_auth

        email: str
        passwd: str
        email, passwd = self.extract_user_credentials(decode_auth)

        if email is None or passwd is None:
            return None

        curr_user = self.user_object_from_credentials(email, passwd)

        return curr_user
