from decimal import Decimal

from database import get_connection
from enums.comparison_operator import ComparisonOperator

OPERATORS = {
    ComparisonOperator.lt: "<",
    ComparisonOperator.gt: ">",
    ComparisonOperator.eq: "=",
}


def get_products(names: list[str], price: Decimal | None, stock: int | None, price_operator: ComparisonOperator | None, stock_operator: ComparisonOperator | None):
    conditions = []
    params = []
    if names:
        name_conditions = ["name LIKE %s" for _ in names]
        conditions.append("(" + " OR ".join(name_conditions) + ")")
        params.extend(f"%{name}%" for name in names)

    if price is not None:
        conditions.append(f"price {OPERATORS[price_operator]} %s")
        params.append(price)

    if stock is not None:
        conditions.append(f"stock_quantity {OPERATORS[stock_operator]} %s")
        params.append(stock)

    query = f"SELECT * FROM products"

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY product_id;"

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


def get_product_by_id(product_id: int):
    query = "SELECT * FROM products WHERE product_id = %s"
    params = [product_id]

    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            return cursor.fetchone()
        finally:
            cursor.close()
    finally:
        connection.close()