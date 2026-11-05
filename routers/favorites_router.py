from typing import Annotated

from fastapi import APIRouter, Depends, Response, HTTPException

from schemas.products_schema import ProductResponse
from security.auth_dependencies import get_current_user
from services import favorites_service
from exceptions.favorite_exceptions import FavoriteAlreadyExistsError, ProductNotFoundError

router = APIRouter(prefix="/favorites", tags=["favorites"])

CurrentUser = Annotated[dict, Depends(get_current_user)]


@router.get("/", response_model=list[ProductResponse])
def list_favorites(current_user: CurrentUser):
    return favorites_service.list_favorites(current_user["user_id"])


@router.post("/{product_id}", status_code=204)
def add_favorite(product_id: int, current_user: CurrentUser) -> Response:
    try:
        favorites_service.add_favorite(current_user["user_id"], product_id)
        return Response(status_code=204)
    except FavoriteAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{product_id}", status_code=204)
def delete_favorite(product_id: int, current_user: CurrentUser) -> Response:
    if not favorites_service.delete_favorite(current_user["user_id"], product_id):
        raise HTTPException(status_code=404, detail="Product is not in your favorites")
    return Response(status_code=204)