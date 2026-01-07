# from sqlalchemy import Column, ForeignKey, Integer, String, Text
# from sqlalchemy.orm import relationship

# from base.models import BaseModel


# class Watchlist(BaseModel):
#     __tablename__ = "watchlists"
#     user_id = Column(
#         String(10),
#         ForeignKey("users.id"),
#         index=True,
#         nullable=False,
#     )
#     stock_id = Column(
#         String(10),
#         ForeignKey("stocks.id"),
#         index=True,
#         nullable=False,
#     )

#     stock = relationship("Stock", back_populates="watchlists")
#     user = relationship("User", back_populates="watchlists")
