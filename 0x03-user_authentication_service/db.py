#!/usr/bin/env python3
"""DB module
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from user import User
from user import Base


class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Add user to database and return a User object
        """
        new_user = User(email=email, hashed_password=hashed_password)
        self._session.add(new_user)
        self._session.commit()

        return new_user

    def find_user_by(self, **kwargs) -> User:
        """find a user
        """
        if not kwargs:
            raise InvalidRequestError

        col_keys = User.__table__.columns.keys()
        for key in kwargs.keys():
            if key not in col_keys:
                raise InvalidRequestError

        users = self._session.query(User).filter_by(**kwargs).first()
        if users is None:
            raise NoResultFound

        return users

    def update_user(self, user_id: int, **kwargs) -> None:
        """Update user data
        """
        if not kwargs:
            return None

        user = self.find_user_by(id=user_id)

        if user is None:
            return None

        col_keys = User.__table__.columns.keys()
        for key in kwargs.keys():
            if key not in col_keys:
                raise ValueError

        for key, val in kwargs.items():
            setattr(user, key, val)

        self._session.commit()
