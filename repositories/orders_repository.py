from database import get_connection
from exceptions.user_exceptions import UserNotFoundError
from exceptions.product_exception import ProductNotFoundError, ProductStockQuantityError

def add_item_to_temp_order(user_id: int, product_id: int, quantity: int) -> int:
    status = "TEMP"
    user_query = "SELECT user_id FROM users WHERE user_id = %s FOR UPDATE"
    user_params = [user_id]
    products_query = "SELECT name, price, stock_quantity FROM products WHERE product_id = %s FOR UPDATE"
    products_params = [product_id]
    is_order_query = "SELECT order_id FROM orders WHERE user_id = %s AND status = 'TEMP'"
    is_order_params = [user_id]
    update_order_total_price_query = "UPDATE orders SET total_price = (SELECT SUM(quantity * unit_price) FROM order_items WHERE order_id = %s) WHERE order_id = %s"

    connection = get_connection()
    try:
        connection.start_transaction()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(user_query, user_params)
            user = cursor.fetchone()
            if user is None:
                raise UserNotFoundError("User not found")

            cursor.execute(products_query, products_params)
            product = cursor.fetchone()
            if product is None:
                raise ProductNotFoundError("Product not found")

            cursor.execute(is_order_query, is_order_params)
            order = cursor.fetchone()
            existing_item = None
            if order is not None:
                existing_order_product_quantity_query = "SELECT quantity FROM order_items WHERE order_id = %s AND product_id = %s"
                cursor.execute(existing_order_product_quantity_query, (order["order_id"], product_id))
                existing_item = cursor.fetchone()

            existing_quantity = existing_item["quantity"] if existing_item else 0
            new_quantity = existing_quantity + quantity
            if product["stock_quantity"] < new_quantity:
                raise ProductStockQuantityError("Product stock quantity exceeds total quantity")

            if order is None:
                create_order_query = "INSERT INTO orders (user_id, status) VALUES (%s, %s)"
                cursor.execute(create_order_query, (user_id, status))
                order_id = cursor.lastrowid
            else:
                order_id = order["order_id"]

            if existing_item is None:
                create_order_to_item_query = "INSERT INTO order_items (order_id, product_id, quantity, product_name, unit_price) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(create_order_to_item_query, (order_id, product_id, new_quantity, product["name"], product["price"]))
            else:
                update_order_to_item_query = "UPDATE order_items set quantity = %s WHERE order_id = %s AND product_id = %s"
                cursor.execute(update_order_to_item_query, (new_quantity, order_id, product_id))

            cursor.execute(update_order_total_price_query, (order_id, order_id))
            connection.commit()
            return order_id
        finally:
            cursor.close()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def get_temp_order(user_id: int) -> dict | None:
    query = """SELECT o.order_id, o.creation_date, o.status, o.shipping_address, o.total_price, i.product_id, i.product_name, i.quantity, i.unit_price 
               FROM orders AS o LEFT JOIN order_items AS i ON o.order_id = i.order_id WHERE o.user_id = %s AND o.status = 'TEMP' ORDER BY i.product_id"""
    params = [user_id]
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()
    finally:
        connection.close()