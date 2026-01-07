from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

from base.models import BaseModel


class Stock(BaseModel):
    __tablename__ = "stocks"
    # __table_args__ = (UniqueConstraint("symbol", name="uq_stock_symbol"),)

    symbol = Column(
        String(10),
        index=True,
        nullable=False,
        unique=True,
    )
    company_name = Column(
        String(255),
        nullable=False,
    )
    price = Column(
        Integer,
        nullable=False,
    )
    last_updated = Column(
        String(50),
        nullable=False,
        default=lambda: datetime.now().isoformat(),
    )

    history = relationship("StockHistory", back_populates="stock")
