from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine("sqlite:///file_records.db")
# SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)


class SessionLocal:
    """单例限制数据库连接数"""

    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = sessionmaker(bind=engine)()
        return cls.__instance


class FileRecord(Base):
    __tablename__ = "file_records"
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True)
    filename = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class MsgRecord(Base):
    __tablename__ = "msg_records"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # pylint: disable=E1101
