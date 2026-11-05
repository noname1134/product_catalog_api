from decimal import Decimal

from repositories.products_repository import get_products as get_products_repositories, get_product_by_id as get_product_by_id_repository
from enums.comparison_operator import ComparisonOperator


def get_products(names: list[str], price: Decimal | None, stock: int | None, price_operator: ComparisonOperator | None, stock_operator: ComparisonOperator | None) -> dict | None:
    return get_products_repositories(names, price, stock, price_operator, stock_operator)


def get_product_by_id(product_id: int) -> dict | None:
    return get_product_by_id_repository(product_id)