from repositories import orders_repository
from schemas.orders_schema import AddOrderItem


def add_item_to_temp_order(user_id: int, item: AddOrderItem) -> int:
    return orders_repository.add_item_to_temp_order(user_id, item.product_id, item.quantity)