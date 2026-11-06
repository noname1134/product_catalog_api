from fastapi import APIRouter, HTTPException

from schemas.orders_schema import AddOrderItem
from services import orders_service
from security.auth_dependencies import CurrentUser
from exceptions.product_exception import ProductNotFoundError, ProductStockQuantityError
from exceptions.user_exceptions import UserNotFoundError


router = APIRouter(prefix="/orders", tags=["orders"])



@router.post("/temp/items")
def add_item_to_temp_order(item: AddOrderItem, current_user: CurrentUser):
    try:
        order_id = orders_service.add_item_to_temp_order(current_user["user_id"], item)
        return {"order_id": order_id}
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProductStockQuantityError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
