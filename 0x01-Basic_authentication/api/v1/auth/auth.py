#!/usr/bin/env python3
""" 
    Authentication module,
        - Authentication class
            - require_auth
                - validates if endpoint requires auth
            - authorization_header
                - handles authorization header
            - current_user
                - validates current user
"""

from flask import request
from typing import List, TypeVar


class Auth:
    """ Class to manage the API authentication """

    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """ Validates if endpoint requires auth """
        if path is None or excluded_paths is None or excluded_paths == []:
            return True

        path_count = len(path) #count of slashes
        if path_count == 0:
            return True

        slash_path = True if path[path_count - 1] == '/' else False

        tmp_path = path #path without slash
        if not slash_path:
            tmp_path += '/'

        for exc in excluded_paths:
            l_exc = len(exc) #count of slashes
            if l_exc == 0:
                continue

            if exc[l_exc - 1] != '*':
                if tmp_path == exc:
                    return False
            else:
                if exc[:-1] == path[:l_exc - 1]:
                    return False

        #if no exclusions, return true
        return True

    def authorization_header(self, request=None) -> str:
        """ Handles authorization header
            - request: request object
        """

        if request is None:
            return None

        return request.headers.get("Authorization", None)

    def current_user(self, request=None) -> TypeVar('User'):
        """ Checks current user
            - request: request object
        """
        return None
