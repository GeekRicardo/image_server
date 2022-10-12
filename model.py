import os
import pymysql
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Text, DateTime

pymysql.install_as_MySQLdb()
engine = create_engine(os.environ["MYSQL_URI"], encoding="utf-8")
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()
Base = declarative_base()


class FileBase(Base):
    __tablename__ = "file"

    md5 = Column(String(255), primary_key=True)
    filename = Column(String(255))
    ctime = Column(Time)

    def __init__(self, md5, filename, ctime=datetime.now()):
        self.md5 = md5
        self.filename = filename
        self.ctime = ctime

    def __str__(self):
        return (
            f"{self.filename} 【{self.md5}】<{self.ctime.strftime('%Y-%m-%d %H:%M:%S')}>"
        )


class Msg(Base):
    __tablename__ = "msg"

    id = Column(Integer, primary_key=True)
    msg = Column(Text)
    ctime = Column(Time)

    def __init__(self, msg, id_=None, ctime=datetime.now()):
        if id_:
            self.id = id_
        self.msg = msg
        self.ctime = ctime

    def __str__(self):
        return f"{self.id} -【{self.msg}】<{self.ctime.strftime('%Y-%m-%d %H:%M:%S')}>"


# 在数据库中生成表
Base.metadata.create_all(bind=engine)
