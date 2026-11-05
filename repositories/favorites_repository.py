from mysql.connector import IntegrityError, errorcode

from database import get_connection
from exceptions.favorite_exceptions import FavoriteAlreadyExistsError


def add_favorite(user_id: int, product_id: int) -> None:
    query = """INSERT INTO favorites (user_id, product_id) VALUES (%s, %s)"""
    params = [user_id, product_id]
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            connection.commit()
        except IntegrityError as exc:
            connection.rollback()
            if exc.errno == errorcode.ER_DUP_ENTRY:
                raise FavoriteAlreadyExistsError(
                    "Product already in favorites"
                ) from exc
            raise
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
    finally:
        connection.close()


def remove_favorite(user_id, product_id) -> bool:
    query = """DELETE FROM favorites WHERE user_id = %s AND product_id = %s"""
    params = [user_id, product_id]
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            deleted_count = cursor.rowcount
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
    finally:
        connection.close()
    return deleted_count > 0


def get_favorites_by_user_id(user_id: int) -> list[dict]:
    query = """SELECT p.product_id, p.name, p.description, p.price, p.stock_quantity
               FROM favorites AS f
                        INNER JOIN products AS p ON f.product_id = p.product_id
               WHERE f.user_id = %s
               ORDER BY p.product_id"""
    params = [user_id]

    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        finally:
            cursor.close()
    finally:
        connection.close()