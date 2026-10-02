from datetime import date
from decimal import Decimal
from typing import Any, Literal
from pydantic import BaseModel, Field, model_validator

Status = Literal["PENDING", "PROCESSING", "SHIPPED"]


class CartItem(BaseModel):
    product_id: str = Field(pattern=r"^[a-fA-F0-9]{24}$")
    quantity: int = Field(ge=1, le=100)


class OrderCreate(BaseModel):
    user_id: int = Field(gt=0)
    items: list[CartItem] = Field(min_length=1, max_length=100)


class StatusUpdate(BaseModel):
    status: Status


class ProductWrite(BaseModel):
    sku: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    price: Decimal = Field(ge=0, le=1000000, max_digits=10, decimal_places=2)
    category: str = Field(min_length=1, max_length=80)
    tags: list[str] = Field(default_factory=list, max_length=30)
    attributes: dict[str, Any] = Field(default_factory=dict)
    variants: list[dict[str, Any]] = Field(min_length=1, max_length=50)
    active: bool = True


class SearchQuery(BaseModel):
    query: str = Field(default="", max_length=200)
    statuses: list[Status] = Field(default_factory=list)
    date_from: date | None = None
    date_to: date | None = None
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)
    page: int = Field(default=1, ge=1, le=500)
    page_size: int = Field(default=10, ge=1, le=20)

    @model_validator(mode="after")
    def check_ranges(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("Start date must be on or before end date")
        if self.min_price is not None and self.max_price is not None and self.min_price > self.max_price:
            raise ValueError("Minimum price must not exceed maximum price")
        return self
