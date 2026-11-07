import logging

from redis.exceptions import RedisError

from repositories import orders_repository
from repositories.products_cache_repository import invalidate_products_cache
from schemas.orders_schema import AddOrderItem

logger = logging.getLogger(__name__)


def add_item_to_temp_order(user_id: int, item: AddOrderItem) -> int:
    return orders_repository.add_item_to_temp_order(user_id, item.product_id, item.quantity)

def get_temp_order(user_id: int) -> dict | None:
    rows = orders_repository.get_temp_order(user_id)
    return create_order_detail_dict(rows)


def list_orders_by_user_id(user_id: int) -> list[dict]:
    return orders_repository.list_orders_by_user_id(user_id)


def get_order_by_id(user_id: int, order_id: int) -> dict | None:
    rows = orders_repository.get_order_by_id(user_id, order_id)
    return create_order_detail_dict(rows)


def remove_item_from_temp_order(user_id, product_id) -> bool:
    return orders_repository.remove_item_from_temp_order(user_id, product_id)


def delete_temp_order(user_id: int) -> bool:
    return orders_repository.delete_temp_order(user_id)


def close_order(user_id: int, order_id: int, shipping_address: str) -> bool:
    is_success = orders_repository.close_order(user_id, order_id, shipping_address)
    if is_success:
        try:
            invalidate_products_cache()
        except RedisError:
            logger.exception("Failed to invalidate product cache after checkout")
    return is_success



def create_order_detail_dict(rows: list[dict]) -> dict | None:
    if not rows:
        return None

    first = rows[0]
    return {
        "order_id": first["order_id"],
        "creation_date": first["creation_date"],
        "status": first["status"],
        "shipping_address": first["shipping_address"],
        "total_price": first["total_price"],
        "items": [
            {
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "quantity": row["quantity"],
                "unit_price": row["unit_price"],
            }
            for row in rows
            if row["product_id"] is not None
        ]
    }