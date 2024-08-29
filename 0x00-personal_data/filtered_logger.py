#!/usr/bin/env python3
"""
Obfuscate log message with regex
Log formatter
Create Logger
"""
import os
import mysql.connector
from typing import List, Tuple
import re
import logging


PII_FIELDS: Tuple = ("email", "phone", "ssn", "password", "ip")


def get_db() -> mysql.connector.connection.MySQLConnection:
    """returns a connector to the mysql database"""
    username = os.getenv('PERSONAL_DATA_DB_USERNAME', 'root')
    password = os.getenv('PERSONAL_DATA_DB_PASSWORD', '')
    host = os.getenv('PERSONAL_DATA_DB_HOST', 'localhost')
    db_name = os.getenv('PERSONAL_DATA_DB_NAME')

    mydb = mysql.connector.connect(
            host=host,
            username=username,
            password=password,
            database=db_name
    )
    return mydb


def filter_datum(fields: List[str], redaction: str, message: str,
                 separator: str) -> str:
    """
    Filter and obfuscate the string

        Args:
            fields: a list of strings representing all fields to obfuscate
                    ["password", "date_of_birth"]
            redaction: a string representing by what the
                       field will be obfuscated
                       "XXX"
            message: a string representing the log line
                    ["name=egg;email=eggmin@eggsample.com;password=eggcellent;date_of_birth=12/12/1986;"]
                    ["name=bob;email=bob@dylan.com;password=bobbycool;date_of_birth=03/04/1993;"]
            separator: a string representing by which character is
                    separating all fields in the log line (message)
                    ";"
        Return:
            String with string obfuscated
    """
    for item in fields:
        message = re.sub(rf'{item}=[^{separator}]+', f'{item}={redaction}',
                         message)
    return message


def get_logger() -> logging.Logger:
    """
    Create logger
    Args: None
    Return: a logging.Logger object
    """
    logger = logging.getLogger('user_data')
    logger.setLevel(logging.INFO)
    logger.propagate = False

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(RedactingFormatter(fields=PII_FIELDS))
    logger.addHandler(stream_handler)

    return logger


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        self.fields = fields
        super(RedactingFormatter, self).__init__(self.FORMAT)

    def format(self, record: logging.LogRecord) -> str:
        record.msg = filter_datum(self.fields, self.REDACTION,
                                  record.getMessage(), self.SEPARATOR)
        return (super(RedactingFormatter, self).format(record))


def main():
    """Entry Point"""
    db: mysql.connector.connection.MySQLConnection = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name, email, phone, ssn, password FROM users;")
    headers: Tuple = (head[0] for head in cursor.description)
    logger: logging.Logger = get_logger()

    for row in cursor:
        data_row: str = ''
        for key, value in zip(headers, row):
            data_row = ''.join(f'{key}={str(value)};')

        logger.info(data_row)

    cursor.close()
    db.close()


if __name__ == '__main__':
    main()
