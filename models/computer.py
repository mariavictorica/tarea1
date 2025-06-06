from config.database import Base
from sqlalchemy import Column, Integer, String, Float

class Computers(Base):
    __tablename__ = "computers"

    id = Column(Integer, primary_key = True)
    brand = Column(String)
    model = Column(String)
    color = Column(String)
    processor = Column(String)
    ram = Column(Integer)
    storage = Column(Integer)
    price = Column(Float)
    category = Column(String)
