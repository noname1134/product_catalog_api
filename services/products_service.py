from decimal import Decimal

from repositories import products_repository
from enums.comparison_operator import ComparisonOperator


def get_products(names: list[str], price: Decimal | None, stock: int | None, price_operator: ComparisonOperator | None, stock_operator: ComparisonOperator | None) -> dict | None:
    return products_repository.get_products(names, price, stock, price_operator, stock_operator)


def get_product_by_id(product_id: int) -> dict | None:
    return products_repository.get_product_by_id(product_id)