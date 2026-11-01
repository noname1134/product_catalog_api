from pydantic import BaseModel, Field
from decimal import Decimal


class ProductResponse(BaseModel):
    product_id: int
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    price: Decimal = Field(gt=0)
    stock_quantity: int = Field(ge=0)