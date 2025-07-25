from sqlalchemy import Column, String, DateTime, func
from db.database import Base
from sqlalchemy.orm import relationship

class AppliedScheme(Base):
    __tablename__ = "applied_schemes"
    reference_id = Column(String, primary_key=True)
    scheme_id = Column(String, index=True)
    farmer_id = Column(String, index=True)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    scheme = relationship("SchemeMaster", backref="applications")

class SchemeMaster(Base):
    __tablename__ = "scheme_master"
    scheme_id = Column(String, primary_key=True)
    scheme_name = Column(String, nullable=False)
    description = Column(String)
    deadline = Column(DateTime, nullable=True, default=None)
    region = Column(String, index=True)
    crop = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
