#!/usr/bin/env python3

"""
    Complete the DB class provided;
    to implement the add_user method.
"""
# pylint: disable=consider-iterating-dictionary

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound

from user import Base, User


class DB:
    """ Initializes the database and creates the users table """

    def __init__(self):
        """ Constructor Method """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self):
        """ A property that returns the session object """
        if self.__session is None:
            session_db = sessionmaker(bind=self._engine)
            self.__session = session_db()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """ Function to add a user to the database """
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()

        return user

    def find_user_by(self, **kwargs) -> User:
        """ Function to find a user by key word args """
        if not kwargs:
            raise InvalidRequestError

        column_names = User.__table__.columns.keys()
        # Check if all the key word args are in the table
        for key in kwargs.keys():
            if key not in column_names:
                raise InvalidRequestError

        user = self._session.query(User).filter_by(**kwargs).first()

        if user is None:
            raise NoResultFound

        return user

    def update_user(self, user_id: int, **kwargs) -> None:
        """ Function to update a user's attributes """

        user = self.find_user_by(id=user_id)

        column_names = User.__table__.columns.keys()
        for key in kwargs.keys():
            if key not in column_names:
                raise ValueError

        for key, value in kwargs.items():
            setattr(user, key, value)

        self._session.commit()
