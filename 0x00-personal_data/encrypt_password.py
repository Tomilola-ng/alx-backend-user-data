#!/usr/bin/env python3
"""
Module for password encryption and validation
"""
import bcrypt


def hash_password(password: str) -> bytes:
    """
    Generates a salted, hashed password.
    The result is returned as a byte string.
    """
    password_bytes = password.encode('utf-8')
    salted_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return salted_hash


def is_valid(hashed_password: bytes, password: str) -> bool:
    """
    Validates if the provided password matches the stored hashed password.
    Returns True if the passwords match, otherwise False.
    """
    password_bytes = password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_password)
