#!/usr/bin/env python3
"""Session Expiration module
"""
from api.v1.auth.session_auth import SessionAuth
from os import getenv
from typing import Dict
from datetime import datetime, timedelta


class SessionExpAuth(SessionAuth):
    """Session Expiration
    """
    def __init__(self):
        """initialization"""
        session_duration = getenv('SESSION_DURATION')

        try:
            session_duration = int(session_duration)
        except Exception:
            session_duration = 0

        self.session_duration = session_duration

    def create_session(self, user_id=None):
        """create new session and register in class with time of creation
        Return session id
        """
        session_id = super().create_session(user_id)
        if session_id is None:
            return None

        session_dictionary: Dict = {
            "user_id": user_id,
            "created_at": datetime.now()
        }
        self.user_id_by_session_id[session_id] = session_dictionary

        return session_id

    def user_id_for_session_id(self, session_id=None):
        """make a user session based on time
        """
        if session_id is None:
            return None
        if session_id not in self.user_id_by_session_id.keys():
            return None

        session_dictionary = self.user_id_by_session_id.get(session_id)

        if self.session_duration <= 0 or session_dictionary is None:
            return session_dictionary.get('user_id', None)

        created_time = session_dictionary.get('created-at', None)
        if created_time is None:
            return None

        expired_sess = created_time + timedelta(seconds=self.session_duration)
        if expired_sess < datetime.now():
            return None

        return session_dictionary.get('user_id', None)
