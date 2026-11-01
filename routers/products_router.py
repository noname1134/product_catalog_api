from fastapi import APIRouter, Query, HTTPException
from typing import Annotated
from decimal import Decimal

from services.products_service import get_products as get_products_service
from schemas.products_schema import ProductResponse
from enums.comparison_operator import ComparisonOperator


router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=list[ProductResponse])
def get_products(names: Annotated[list[str], Query(alias="name")] = [],
                 price: Annotated[Decimal | None, Query(ge=0)] = None,
                 stock: Annotated[int | None, Query(ge=0)] = None,
                 price_operator: ComparisonOperator | None = None,
                 stock_operator: ComparisonOperator | None = None):
    if price is not None and price_operator is None:
        raise HTTPException(status_code=422, detail="price_operator is required when price is provided")
    if price is None and price_operator is not None:
        raise HTTPException(status_code=422, detail="price is required when price_operator is provided")
    if stock is not None and stock_operator is None:
        raise HTTPException(status_code=422, detail="stock_operator is required when stock is provided")
    if stock is None and stock_operator is not None:
        raise HTTPException(status_code=422, detail="stock is required when stock_operator is provided")

    return get_products_service(names, price, stock, price_operator, stock_operator)
