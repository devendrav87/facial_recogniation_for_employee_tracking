from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
import os

# Create the database directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Initialize database with thread-safe session
engine = create_engine('sqlite:///data/attendance.db', connect_args={'check_same_thread': False})
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    face_encoding = Column(String, nullable=False)  # Stored as pickled numpy array
    attendances = relationship('Attendance', back_populates='employee')
    reports = relationship('DailyReport', back_populates='employee')

class Attendance(Base):
    __tablename__ = 'attendances'
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    event_type = Column(String(10), nullable=False)  # 'entry' or 'exit'
    employee = relationship('Employee', back_populates='attendances')

class DailyReport(Base):
    __tablename__ = 'daily_reports'
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    total_hours = Column(Float, nullable=False)
    employee = relationship('Employee', back_populates='reports')

# Create all tables
Base.metadata.create_all(engine)
