from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field
from decimal import Decimal


class AddOrderItem(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal


class TempOrderResponse(BaseModel):
    order_id: int
    creation_date: datetime
    status: Literal["TEMP"]
    shipping_address: str | None
    total_price: Decimal
    items: list[OrderItemResponse]


class OrdersResponse(BaseModel):
    order_id: int
    creation_date: datetime
    status: Literal["TEMP", "CLOSE"]
    shipping_address: str | None
    total_price: Decimal


class OrderDetailResponse(OrdersResponse):
    items: list[OrderItemResponse]


class CheckoutOrder(BaseModel):
    shipping_address: str = Field(min_length=1, max_length=255, str_strip=True)