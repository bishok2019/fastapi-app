from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class StockListSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    company_name: str
    price: int
    last_updated: str


class StockCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    company_name: str
    price: int
    last_updated: Optional[datetime] = None


class StockUpdateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    company_name: str
    price: int
    last_updated: str


class StockRetrieveSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    company_name: str
    price: int
    last_updated: str
