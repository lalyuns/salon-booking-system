from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base, engine

# 多對多關聯表 (預約與服務)
appointment_services = Table(
    "appointment_services",
    Base.metadata,
    Column("appointment_id", Integer, ForeignKey("appointments.id"), primary_key=True),
    Column("service_id", Integer, ForeignKey("services.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    line_id = Column(String(255), unique=True, index=True)
    name = Column(String(100))
    phone = Column(String(20))
    appointments = relationship("Appointment", back_populates="user")

class Designer(Base):
    __tablename__ = "designers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    appointments = relationship("Appointment", back_populates="designer")

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    duration = Column(Integer)  # 耗時(分鐘)

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    designer_id = Column(Integer, ForeignKey("designers.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="appointments")
    designer = relationship("Designer", back_populates="appointments")
    services = relationship("Service", secondary=appointment_services)

# 執行這行會在資料庫中自動建立所有表格
Base.metadata.create_all(bind=engine)
print("資料庫表格初始化完成！")