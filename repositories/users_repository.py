from mysql.connector import IntegrityError, errorcode

from database import get_connection
from schemas.users_schema import UserCreate
from exceptions.user_exceptions import UserAlreadyExistsError


def create_user(user: UserCreate, password_hash: str) -> int:
    query = "INSERT INTO users (username, password_hash, first_name, last_name, email, phone, country, city) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    params = [user.username, password_hash, user.first_name, user.last_name, user.email, user.phone, user.country, user.city]

    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            user_id = cursor.lastrowid
            connection.commit()
            return user_id
        except IntegrityError as exc:
            connection.rollback()
            if exc.errno == errorcode.ER_DUP_ENTRY:
                raise UserAlreadyExistsError(
                    "Username or email already exists"
                ) from exc
            raise
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
    finally:
        connection.close()


def get_user_by_id(user_id: int):
    query = "SELECT user_id, username, first_name, last_name, email, phone, country, city FROM users WHERE user_id = %s"
    params = [user_id]
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result
        finally:
            cursor.close()
    finally:
        connection.close()


def get_user_by_username(username: str):
    query = "SELECT user_id, username, password_hash FROM users WHERE username = %s"
    params = [username]
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result
        finally:
            cursor.close()
    finally:
        connection.close()