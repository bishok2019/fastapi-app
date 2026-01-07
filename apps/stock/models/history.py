from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from base.models import BaseModel


class StockHistory(BaseModel):
    __tablename__ = "stock_history"
    stock_id = Column(
        Integer,
        ForeignKey("stocks.id"),
        index=True,
        nullable=False,
    )
    price = Column(Integer, nullable=False)

    stock = relationship("Stock", back_populates="history")
