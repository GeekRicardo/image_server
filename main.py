#!/usr/bin python
# -*- encoding: utf-8 -*-
"""
@File    :   main.py
@Time    :   2021/11/04 18:13:24
@Author  :   Ricardo
@Version :   1.0
@Contact :   GeekRicardozzZ@gmail.com
@Desc    :   图片上传服务器
"""

# here put the import lib
import os
import uuid
from datetime import datetime

import logging
import uvicorn
from fastapi import (
    Depends,
    FastAPI,
    Form,
    File,
    Request,
    Response,
    UploadFile,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from rich.logging import RichHandler

from model import Base, FileRecord, MsgRecord, SessionLocal, engine, get_db
from filters import datetime_format, format_size

FORMAT = "%(message)s"
logging.basicConfig(level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])

logger = logging.getLogger("main")

app = FastAPI()
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
templates = Jinja2Templates(directory="templates")
templates.env.filters.update({"datetime_format": datetime_format, "format_size": format_size})


UPLOAD_DIR = "uploads"


@app.post("/upload/")
async def upload(uploaded_file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 保存上传的文件
    uuid_filename = str(uuid.uuid4())
    with open(f"{UPLOAD_DIR}/{uuid_filename}", "wb") as f:
        f_bytes = uploaded_file.file.read()
        f.write(f_bytes)

    # 保存上传记录到数据库
    add_file = FileRecord(
        filename=uploaded_file.filename,
        uuid=uuid_filename,
        created_at=datetime.utcnow(),
    )
    db.add(add_file)
    db.commit()
    db.refresh(add_file)
    # return RedirectResponse(url=app.url_path_for("index"), status_code=302)
    return HTMLResponse(
        f"<tr><td><a href='/{add_file.uuid}' target='_blank'>{add_file.uuid}"
        + f"</a></td><td>{add_file.filename}</td><td>Now</td><td>{uploaded_file.size}</td></tr>"
    )


@app.post("/send/")
async def send_msg(message: str = Form(...), db: Session = Depends(get_db)):
    new_msg = MsgRecord(message=message, created_at=datetime.utcnow())
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return RedirectResponse(url=app.url_path_for("index"), status_code=302)


@app.get("/msg")
async def get_msg(db: Session = Depends(get_db)):
    msg_list = db.query(MsgRecord).order_by(MsgRecord.created_at.desc()).all()
    return templates.TemplateResponse("message.html", {"msgs": msg_list})


# @app.get("/list")
# async def file_list(db: Session = Depends(get_db)):
#     files = db.query(FileRecord).order_by(FileRecord.created_at.desc()).all()
#     file_list = []
#     for file in files:
#         file_path = os.path.join(UPLOAD_DIR, file.uuid)
#         file_size = os.path.getsize(file_path)
#         file_list.append(
#             {
#                 "name": file.uuid,
#                 "original_name": file.filename,
#                 "created_at": file.created_at,
#                 "size": file_size,
#             }
#         )
#     return templates.TemplateResponse("list.html", {"files": file_list})


@app.get("/")
async def index(request: Request, db: Session = Depends(get_db)):
    # 查询所有文件，按照上传时间排序
    files = db.query(FileRecord).order_by(FileRecord.created_at.desc()).all()
    msg_list = db.query(MsgRecord).order_by(MsgRecord.created_at.desc()).limit(5).all()

    # 构建文件列表数据，包括文件名、原文件名、上传时间、文件大小等信息
    file_list = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        file_size = os.path.getsize(file_path)
        file_list.append(
            {
                "name": file.uuid,
                "original_name": file.filename,
                "created_at": file.created_at,
                "size": file_size,
            }
        )

    # 渲染文件列表模板
    return templates.TemplateResponse("index.html", {"request": request, "files": file_list, "msgs": msg_list})


@app.get("/{filename}")
async def download(filename: str, d: str = "", db: Session = Depends(get_db)):
    # 根据UUID查询上传文件记录
    upload_file = db.query(FileRecord).filter(FileRecord.uuid == filename).first()

    # 如果上传文件记录不存在，则返回404
    if not upload_file:
        logger.error("文件不存在")
        return Response(status_code=404, content="文件不存在", media_type="text/plain")

    # 获取上传文件的本地路径
    file_path = os.path.join(UPLOAD_DIR, upload_file.uuid)

    # 如果上传文件不存在，则返回404
    if not os.path.exists(file_path):
        logger.error("文件被移动或删除")
        return Response(status_code=404, content="文件被移动或删除", media_type="text/plain")

    # 读取上传文件内容
    with open(file_path, "rb") as f:
        file_content = f.read()

    # 构造HTTP响应
    file_extension = upload_file.filename.rsplit(".", 1)[-1].lower()
    media_type = get_media_type(file_extension, d)
    response = Response(content=file_content, media_type=media_type)
    if d == "1":
        # 设置下载时的文件名
        response.headers["Content-Disposition"] = f"attachment; filename={upload_file.filename}"

    return response


def get_media_type(file_extension: str, direct_download: str = "") -> str:
    media_type = "application/octet-stream"
    if direct_download == "1":
        media_type = "application/octet-stream"
    elif file_extension in ["jpg", "jpeg"]:
        media_type = "image/jpeg"
    elif "png" == file_extension:
        media_type = "image/png"
    elif "txt" == file_extension:
        media_type = "text/plain"
    elif "pdf" == file_extension:
        media_type = "application/pdf"
    elif "json" == file_extension:
        media_type = "application/json"
    elif "gif" == file_extension:
        media_type = "image/gif"
    return media_type


# pylint: disable=no-member
@app.on_event("startup")
def startup():
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if not db.query(FileRecord).filter(FileRecord.uuid == "favicon.ico").first():
        icon = FileRecord(uuid="favicon.ico", filename="favicon.ico", created_at=datetime.utcnow())
        db.add(icon)
        db.commit()
        db.refresh(icon)


# TODO 消息队列

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "3001")),
        reload=bool(os.getenv("DEBUG", "false")),
        # debug=bool(os.getenv("DEBUG", False)),
        # ssl_keyfile="/root/image_server/ssl/image.sshug.cn.key",
        # ssl_certfile="/root/image_server/ssl/image.sshug.cn_bundle.crt"
    )
