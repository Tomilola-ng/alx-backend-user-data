#!/usr/bin/env python3

"""
    Define a _hash_password method;
    it takes in a password string argument
    returns bytes.
"""

# pylint: disable=raise-missing-from

from uuid import uuid4
from typing import Union

import bcrypt

from sqlalchemy.orm.exc import NoResultFound

from db import DB
from user import User


def _hash_password(password: str) -> str:
    """ Function to hash a password using bcrypt """

    hash_pwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hash_pwd


def _generate_uuid() -> str:
    """ Function to generate a unique ID """

    unique_id = uuid4()
    return str(unique_id)


class Auth:
    """ Auth class to interact with the authentication database. """

    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """ Function to register a user in the database """

        try:
            user_obj = self._db.find_user_by(email=email)
        except NoResultFound:
            hashed_password = _hash_password(password)
            user_obj = self._db.add_user(email, hashed_password)

            return user_obj

        else:
            raise ValueError(f'User {email} already exists')

    def valid_login(self, email: str, password: str) -> bool:
        """
            Function to check if a user is valid
            on email and password
        """

        try:
            user_obj = self._db.find_user_by(email=email)
        except NoResultFound:
            return False

        user_pwd = user_obj.hashed_password
        encoded_password = password.encode()

        if bcrypt.checkpw(encoded_password, user_pwd):
            return True

        return False

    def create_session(self, email: str) -> str:
        """ Function to create a session ID for a user """

        try:
            user_obj = self._db.find_user_by(email=email)
        except NoResultFound:
            return None

        session_id = _generate_uuid()

        self._db.update_user(user_obj.id, session_id=session_id)

        return session_id

    def get_user_from_session_id(self, session_id: str) -> Union[str, None]:
        """ Function to get a user from a session ID """
        if session_id is None:
            return None

        try:
            user_obj = self._db.find_user_by(session_id=session_id)
        except NoResultFound:
            return None

        return user_obj

    def destroy_session(self, user_id: int) -> None:
        """Function to destroy a session ID for a user """
        try:
            user = self._db.find_user_by(id=user_id)
        except NoResultFound:
            return None

        self._db.update_user(user.id, session_id=None)

        return None

    def get_reset_password_token(self, email: str) -> str:
        """ Function to generate a reset password token if user exists """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            raise ValueError

        reset_token = _generate_uuid()

        self._db.update_user(user.id, reset_token=reset_token)

        return reset_token

    def update_password(self, reset_token: str, password: str) -> None:
        """ Function to use reset token to validate update of users password """
        if reset_token is None or password is None:
            return None

        try:
            user = self._db.find_user_by(reset_token=reset_token)
        except NoResultFound:
            raise ValueError

        hashed_pwd = _hash_password(password)
        self._db.update_user(user.id,
                             hashed_password=hashed_pwd,
                             reset_token=None)
