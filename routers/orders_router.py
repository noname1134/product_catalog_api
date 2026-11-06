from fastapi import APIRouter, HTTPException, Response

from schemas.orders_schema import AddOrderItem, TempOrderResponse, CheckoutOrder
from services import orders_service
from security.auth_dependencies import CurrentUser
from exceptions.product_exception import ProductNotFoundError, ProductStockQuantityError
from exceptions.user_exceptions import UserNotFoundError
from exceptions.order_exceptions import OrderNotFound, EmptyOrderError


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


@router.post("/{order_id}/checkout", status_code=204)
def close_order(order_id: int, checkout: CheckoutOrder, current_user: CurrentUser):
    try:
        if not orders_service.close_order(current_user["user_id"], order_id, checkout.shipping_address):
            raise HTTPException(status_code=409, detail="Item not in stock")
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except OrderNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except EmptyOrderError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/temp", response_model=TempOrderResponse)
def get_temp_order(current_user: CurrentUser):
    tmp_order = orders_service.get_temp_order(current_user["user_id"])
    if not tmp_order:
        raise HTTPException(status_code=404, detail="No pending order")
    return tmp_order


@router.delete("/temp/{product_id}", status_code=204)
def remove_item_from_temp_order(product_id: int, current_user: CurrentUser) -> Response:
    if not orders_service.remove_item_from_temp_order(current_user["user_id"], product_id):
        raise HTTPException(status_code=404, detail="Item not found in your pending order")
    return Response(status_code=204)


@router.delete("/temp", status_code=204)
def delete_temp_order(current_user: CurrentUser) -> Response:
    if not orders_service.delete_temp_order(current_user["user_id"]):
        raise HTTPException(status_code=404, detail="No pending order")
    return Response(status_code=204)
