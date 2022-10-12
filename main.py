#!/usr/bin python
# -*- encoding: utf-8 -*-
"""
@File    :   Untitled-1
@Time    :   2021/11/04 18:13:24
@Author  :   Ricardo
@Version :   1.0
@Contact :   GeekRicardozzZ@gmail.com
@Desc    :   图片上传服务器
"""

# here put the import lib
from datetime import datetime
from genericpath import isfile
from typing import Optional
from fastapi import FastAPI, Header, File, UploadFile, Response
from fastapi.responses import FileResponse, HTMLResponse

import uvicorn

import os
import hashlib
import uuid

from model import session, FileBase, Msg

app = FastAPI()


# 设置图片保存文件夹
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# 设置允许上传的文件格式
ALLOW_EXTENSIONS = ["png", "jpg", "jpeg", "exe", "pdf", "gif", "txt", "json"]
ALLOW_TOKEN = False

TOKEN_LIST = [
    "1fa81717-2bbc-4dca-a00f-887ebe7c2596",
    "af3d24f83456f002d5ab9918b6317ba0",
]


def allowed_file(filename):
    """
    判断文件后缀是否在列表中
    """
    if not ALLOW_TOKEN:
        return True
    return "." in filename and filename.rsplit(".", 1)[-1] in ALLOW_EXTENSIONS


@app.get("/")
def index():
    return HTMLResponse(
        """<form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file" id="file">
        <input type="submit" value="上传">
    </form>"""
    )


@app.get("/list")
def get_file_list():
    file_list = get_file_list_sortby_mtime()
    return HTMLResponse(
        """<ul>{}</ul>""".format(
            "".join(
                [
                    f"<li><a href=\"/{it.md5}\">{it.filename} - <{it.ctime.strftime('%Y-%m-%d %H:%M:%S')}></a></li>"
                    for it in file_list
                ]
            )
        )
    )


@app.get("/uuid4")
async def get_uuid():
    return Response(content=str(uuid.uuid4()), status_code=200)


@app.post("/upload")
async def uploads(file: UploadFile = File(...)):

    if file and allowed_file(file.filename):
        image_bytes = await file.read()
        md5 = hashlib.md5()
        md5.update(image_bytes[:])
        file_md5 = md5.hexdigest()
        filename = file_md5
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(save_path):
            with open(save_path, "wb") as f:
                f.write(image_bytes)
            new_file = FileBase(file_md5, file.filename, datetime.now())
            session.add(new_file)
            session.commit()
            return Response(status_code=200, content=filename)
        return Response(
            status_code=200, content={"code": 0, "message": "文件已存在", "data": file_md5}
        )
    else:
        return Response(status_code=405, content="not allowed file type")


@app.get("/{imageId}")
async def get_frame(imageId: str, d: str = "", response=Response()):
    if not imageId in os.listdir(UPLOAD_FOLDER):
        response.status_code = 404
        response.content = {"code": -1, "msg": "file not found."}
        return response
    try:
        file_ = session.query(FileBase).filter(FileBase.md5 == imageId).one()
    except Exception as e:
        response.status_code = 404
        response.content = {"code": -1, "msg": "img not found."}
        return response
    media_type = "application/octet-stream"
    file_extension = imageId.rsplit(".", 1)[-1].lower()
    if d == "1":
        media_type = "application/octet-stream"
    elif "jpg" == file_extension or "jpeg" == file_extension:
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
    return FileResponse(
        "{}/{}".format(UPLOAD_FOLDER, imageId),
        media_type=media_type,
        filename=file_.filename,
    )


@app.get("/static/{filename}")
def get_static_file(filename: str, d="", response=Response()):
    if not os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
        response.status_code = 404
        response.content = {"code": -1, "msg": "file not found."}
        return response
    media_type = "application/octet-stream"
    file_extension = filename.rsplit(".", 1)[-1].lower()
    if d == "1":
        media_type = "application/octet-stream"
    elif "jpg" == file_extension or "jpeg" == file_extension:
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
    return FileResponse(
        "{}/{}".format(UPLOAD_FOLDER, filename),
        media_type=media_type,
    )


def get_file_list_sortby_mtime():
    return sorted(session.query(FileBase), key=lambda x: x.ctime, reverse=True)


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 3001)),
        reload=bool(os.getenv("DEBUG", False)),
        debug=bool(os.getenv("DEBUG", False)),
    )
