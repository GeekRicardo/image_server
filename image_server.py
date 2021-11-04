#!/usr/bin python
# -*- encoding: utf-8 -*-
"""
@File    :   Untitled-1
@Time    :   2021/11/04 18:13:24
@Author  :   Ricardo.张葆杰
@Version :   1.0
@Contact :   bj.zhang@tianrang-inc.com
@Desc    :   图片上传服务器
"""

# here put the import lib
from flask import Flask, Response, request, render_template, jsonify
from werkzeug.utils import secure_filename
import os
import hashlib
import uuid

app = Flask(__name__)


# 设置图片保存文件夹
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# 设置允许上传的文件格式
ALLOW_EXTENSIONS = ["png", "jpg", "jpeg"]


# 判断文件后缀是否在列表中
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[-1] in ALLOW_EXTENSIONS


# 上传图片
@app.route("/upload", methods=["POST", "GET"])
def uploads():
    if request.method == "POST":
        # 获取post过来的文件名称，从name=file参数中获取
        file = request.files["file"]
        if file and allowed_file(file.filename):
            print(file.filename)
            # secure_filename方法会去掉文件名中的中文
            # file_md5 = hashlib.md5(
            #     secure_filename(file.filename.encode("utf-8"))
            # ).hexdigest()
            file_md5 = str(uuid.uuid4())
            file_name = file_md5 + "." + file.filename.rsplit(".", 1)[-1]
            # 保存图片
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], file_name))
            return file_name
        else:
            return "-1"
    return render_template("index.html")


# 查看图片
@app.route("/<imageId>")
def get_frame(imageId):
    # 图片上传保存的路径
    with open(
        r"{}/{}".format(UPLOAD_FOLDER, imageId),
        "rb",
    ) as f:
        print(imageId)
        image = f.read()
        filetype = "png" if "png" == imageId.rsplit(".")[-1] else "jpeg"
        resp = Response(image, mimetype="image/" + filetype)
        return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5800, debug=True)
