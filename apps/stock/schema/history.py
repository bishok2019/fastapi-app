from pydantic import BaseModel, ConfigDict


class StockHistoryListSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stock_id: str
    price: int
    created_at: str
