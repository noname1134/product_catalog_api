from repositories import favorites_repository
from repositories.products_repository import get_product_by_id
from exceptions.product_exception import ProductNotFoundError


def list_favorites(user_id: int) -> list[dict]:
    return favorites_repository.get_favorites_by_user_id(user_id)


def add_favorite(user_id: int, product_id: int) -> None:
    if get_product_by_id(product_id) is None:
        raise ProductNotFoundError("Product not found")

    favorites_repository.add_favorite(user_id, product_id)


def delete_favorite(user_id: int, product_id: int) -> bool:
    return favorites_repository.remove_favorite(user_id, product_id)