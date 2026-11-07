from decimal import Decimal

from repositories import products_repository, products_cache_repository
from enums.comparison_operator import ComparisonOperator


def get_products(names: list[str], price: Decimal | None, stock: int | None, price_operator: ComparisonOperator | None, stock_operator: ComparisonOperator | None) -> list[dict]:
    has_filters = (
            bool(names)
            or price is not None
            or stock is not None
            or price_operator is not None
            or stock_operator is not None
    )
    if has_filters:
        return products_repository.get_products(names, price, stock, price_operator, stock_operator)

    products = products_cache_repository.get_cached_products()
    if products is None:
        products = products_repository.get_products(names, price, stock, price_operator, stock_operator)
        products_cache_repository.cache_products(products)

    return products


def get_product_by_id(product_id: int) -> dict | None:
    return products_repository.get_product_by_id(product_id)