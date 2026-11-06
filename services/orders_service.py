from repositories import orders_repository
from schemas.orders_schema import AddOrderItem


def add_item_to_temp_order(user_id: int, item: AddOrderItem) -> int:
    return orders_repository.add_item_to_temp_order(user_id, item.product_id, item.quantity)

def get_temp_order(user_id: int) -> dict | None:
    rows = orders_repository.get_temp_order(user_id)
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


def remove_item_from_temp_order(user_id, product_id) -> bool:
    return orders_repository.remove_item_from_temp_order(user_id, product_id)
