from datetime import datetime
from sqlalchemy import TIMESTAMP, String, Integer, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class AppEvent(Base):
    __tablename__ = "metrics"

    window_start: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), primary_key=True)
    event_type: Mapped[str] = mapped_column(String, primary_key=True)
    count: Mapped[int] = mapped_column(Integer)
    total_value: Mapped[float] = mapped_column(Float)
    unique_users: Mapped[int] = mapped_column(Integer)
    window_size: Mapped[str] = mapped_column(String)