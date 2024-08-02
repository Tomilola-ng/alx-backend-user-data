#!/usr/bin/env python3
"""
    Module for managing and redacting personal data in logs.
"""
from typing import List
import re
import logging
from os import environ
import mysql.connector


# List of personal identifiable information fields to be redacted
PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def filter_datum(fields: List[str], redaction: str,
                          message: str, separator: str) -> str:
    """Redacts specified fields in a log message."""
    for field in fields:
        message = re.sub(f'{field}=.*?{separator}',
                         f'{field}={redaction}{separator}', message)
    return message


def get_logger() -> logging.Logger:
    """Creates and returns a logger with custom formatting."""
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(SensitiveDataFormatter(list(PII_FIELDS)))
    logger.addHandler(stream_handler)

    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """Establishes and returns a connection to the MySQL database."""
    username = environ.get("PERSONAL_DATA_DB_USERNAME", "root")
    password = environ.get("PERSONAL_DATA_DB_PASSWORD", "")
    host = environ.get("PERSONAL_DATA_DB_HOST", "localhost")
    database_name = environ.get("PERSONAL_DATA_DB_NAME")

    connection = mysql.connector.connect(user=username,
                                         password=password,
                                         host=host,
                                         database=database_name)
    return connection


def main():
    """
    Connects to the database, retrieves all rows from the users table,
    and logs each row with sensitive information redacted.
    """
    db_connection = get_db()
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM users;")
    column_names = [column[0] for column in cursor.description]

    logger = get_logger()

    for row in cursor:
        row_str = ''.join(f'{column}={str(value)}; ' 
                          for value, column in zip(row, column_names))
        logger.info(row_str.strip())

    cursor.close()
    db_connection.close()


class SensitiveDataFormatter(logging.Formatter):
    """Formatter class for redacting sensitive information."""

    REDACTION = "***"
    FORMAT = "[SYSTEM] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(SensitiveDataFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """Redacts sensitive data from log messages."""
        record.msg = filter_datum(self.fields, self.REDACTION,
                                           record.getMessage(), self.SEPARATOR)
        return super(SensitiveDataFormatter, self).format(record)


if __name__ == '__main__':
    main()
