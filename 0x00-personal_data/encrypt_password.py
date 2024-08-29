#!/usr/bin/env python3
"""
Encrypting Passwords
"""
import bcrypt


def hash_password(password: str) -> bytes:
    """
    Hashes a password using bcrypt with salt

    Args:
        Password(str): the pasword to hash

    Returns:
        bytes: The salted, hashed password as a byte string
    """
    # convert password to byte
    passwd_bytes = password.encode('utf-8')
    # Generate a salt and hash password with the salt
    salt = bcrypt.gensalt()
    hashed_passwd = bcrypt.hashpw(passwd_bytes, salt)

    return hashed_passwd


def is_valid(hashed_password: bytes, password: str) -> bool:
    """
    Check password validity

    Args:
        hashed_password: the hashed password
        password: the password to check

    Returns:
        True if valid else False
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
