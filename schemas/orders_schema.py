from pydantic import BaseModel, Field


class AddOrderItem(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)