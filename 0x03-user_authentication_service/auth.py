#!/usr/bin/env python3
""" Hash password
"""
import bcrypt
from db import DB
from user import Base, User
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError
from uuid import uuid4


def _hash_password(password: str) -> bytes:
    """hash given password"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(password_bytes, salt)

    hash_str: str = str(hashed_pwd.decode())
    return hash_str


class Auth:
    """Auth class to interact with the authentication database.
    """
    def __init__(self):
        """initialize"""
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """register new user in database"""
        try:
            user = self._db.find_user_by(email=email)
            raise ValueError(f'User {user.email} already exists')
        except NoResultFound:
            hashed_pwd: str = _hash_password(password)
            user = self._db.add_user(email, hashed_pwd)

        return user

    def valid_login(self, email: str, password: str):
        """validate login credentials"""
        if email is None or password is None:
            return False

        try:
            user: User = self._db.find_user_by(email=email)
            hashed_pwd: bytes = str.encode(user.hashed_password)
            is_valid_pswd: bool = bcrypt.checkpw(password.encode('utf-8'),
                                                 hashed_pwd)
            return is_valid_pswd
        except NoResultFound:
            return False

    def _generate_uuid(self) -> str:
        """Generates a UUID as a string"""
        return str(uuid4())

    def create_session(self, email: str) -> str:
        """returns the session ID as a string"""
        try:
            user = self._db.find_user_by(email=email)
            session_id = self._generate_uuid()
            self._db.update_user((user.id), session_id=session_id)
            return session_id
        except NoResultFound:
            return None

    def get_user_from_session_id(self, session_id: str) -> User:
        """returns corresponding user of a session id"""
        if not session_id:
            return None

        try:
            user = self._db.find_user_by(session_id=session_id)
            return user
        except (NoResultFound, InvalidRequestError):
            return None

    def destroy_session(self, user_id: int) -> None:
        """destroy session corresponding to a user id"""
        try:
            user = self._db.update_user(user_id, session_id=None)
        except ValueError:
            return None

    def get_reset_password_token(self, email: str) -> str:
        """Generate reset password token"""
        if email is None:
            raise ValueError

        try:
            user = self._db.find_user_by(email=email)
            token: str = self._generate_uuid()
            self._db.update_user((user.id), reset_token=token)
            return token
        except (NoResultFound, InvalidRequestError):
            raise ValueError

    def update_password(self, reset_token: str, password: str) -> None:
        """update password"""
        if reset_token is None or password is None:
            return None

        try:
            user = self.find_user_by(reset_token=reset_token)
            hash_pwd = _hash_password(password)
            self._db.update_user((user.id), hashed_password=hash_pwd,
                                 reset_token=None)
        except (NoResultFound, InvalidRequestError):
            raise ValueError
