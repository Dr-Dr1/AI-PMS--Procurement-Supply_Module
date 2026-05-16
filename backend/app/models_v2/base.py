"""
Shared SQLAlchemy declarative base — imported by database.py and all model files.
Single Base instance ensures all models share one metadata registry.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
