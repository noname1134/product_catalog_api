from decimal import Decimal

from repositories.products_repository import get_all_products
from enums.comparison_operator import ComparisonOperator


def get_products(names: list[str], price: Decimal | None, stock: int | None, price_operator: ComparisonOperator | None, stock_operator: ComparisonOperator | None):
    return get_all_products(names, price, stock, price_operator, stock_operator)
