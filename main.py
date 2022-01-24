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
from typing import Optional
from fastapi import FastAPI, Header, File, UploadFile, Response
from fastapi.responses import FileResponse

import uvicorn

import os
import hashlib
import uuid

app = FastAPI()


# 设置图片保存文件夹
UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "images"
)
# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# 设置允许上传的文件格式
ALLOW_EXTENSIONS = ["png", "jpg", "jpeg", "exe"]

TOKEN_LIST = [
    "1fa81717-2bbc-4dca-a00f-887ebe7c2596",
    "af3d24f83456f002d5ab9918b6317ba0"
]


def allowed_file(filename):
    """
    判断文件后缀是否在列表中
    """
    return "." in filename and filename.rsplit(".", 1)[-1] in ALLOW_EXTENSIONS


@app.get("/uuid4")
async def get_uuid():
    return Response(content=str(uuid.uuid4()), status_code=200)


@app.post("/upload")
async def uploads(
    file: UploadFile = File(...),
    PToken: Optional[str] = Header(None)
):
    # 验证token
    if not PToken or PToken not in TOKEN_LIST:
        return Response(status_code=401)

    if file and allowed_file(file.filename):
        image_bytes = await file.read()
        md5 = hashlib.md5()
        md5.update(image_bytes[:])
        file_md5 = md5.hexdigest()
        # file_md5 = str(uuid.uuid4())
        file_name = file_md5 + "." + file.filename.rsplit(".", 1)[-1]
        save_path = os.path.join(UPLOAD_FOLDER, file_name)
        if not os.path.exists(save_path):
            with open(save_path, "wb") as f:
                f.write(image_bytes)
        return Response(status_code=200, content=file_name)
    else:
        return Response(status_code=405, content="")


# 查看图片
@app.get("/{imageId}")
async def get_frame(imageId, response=Response()):
    if not os.path.exists(os.path.join(UPLOAD_FOLDER, imageId)):
        response.status_code = 404
        response.content = {"code": -1, "msg": "img not found."}
        return response
    return FileResponse(
        "{}/{}".format(UPLOAD_FOLDER, imageId),
        media_type="image/jpg"
    )


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=3001,
    )
