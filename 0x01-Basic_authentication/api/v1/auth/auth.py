#!/usr/bin/env python3
"""manage API authentication
"""
from flask import request
from typing import List, TypeVar


class Auth:
    """Auth Class

    Methods:
      - require_auth
      - authorization_header
      - current_user
    """
    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """require the authorization"""
        if path is None:
            return True
        if excluded_paths is None or excluded_paths == []:
            return True
        if path[-1] != '/':
            path += '/'
        for paths in excluded_paths:
            if paths.endswith('*'):
                if path.startswith(paths[:-1]):
                    return False
            elif path == paths:
                return False
        return True

    def authorization_header(self, request=None) -> str:
        """get authorization header"""
        if request is None:
            return None

        return request.headers.get("Authorization", None)

    def current_user(self, request=None) -> TypeVar('User'):
        """check requested user"""
        return request
