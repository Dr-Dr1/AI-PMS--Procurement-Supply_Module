from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String
from app.core.database import Base
class ProcurementOrder(Base):
    __tablename__="procurement_orders"
    id:Mapped[int]=mapped_column(primary_key=True, autoincrement=True)
    title:Mapped[str]=mapped_column(String(255))
    status:Mapped[str]=mapped_column(String(50), default="OPEN")
