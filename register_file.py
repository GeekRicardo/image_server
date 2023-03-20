#!/User/ricardo/anaconda3/bin/python
# -*- encoding: utf-8 -*-
"""
@File     :  register_file.py
@Time     :  2023/03/19 10:13:06
@Author   :  Ricardo
@Version  :  1.0
@Desc     :  注册文件到数据库
"""

# import lib here
import os
import re
import argparse
from datetime import datetime
import uuid
from rich.progress import track

from model import FileRecord, SessionLocal, Base, engine
from main import UPLOAD_DIR


# pylint: disable=no-member
def register_folder(folder_path):
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    for file_name in track(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and not exclude_file(args.exclude, file_name):
            file_record = FileRecord(
                uuid=str(uuid.uuid4()),
                filename=file_name,
                created_at=datetime.fromtimestamp(os.stat(file_path).st_ctime),
            )
            db.add(file_record)
            db.commit()
            db.refresh(file_record)
            # 拷贝文件
            cmd = "cp" if os.path.abspath(folder_path) != os.path.abspath(UPLOAD_DIR) else "mv"
            os.system(f"{cmd} {file_path} {UPLOAD_DIR}/{file_record.uuid}")


def exclude_file(reg: str, file_name: str) -> bool:
    """使用正则排除文件"""
    return bool(re.search(reg, file_name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Register files in a folder")
    parser.add_argument("folder_path", type=str, help="Path to folder containing files to register")
    # 添加排除文件名的正则参数
    parser.add_argument("-e", "--exclude", type=str, help="Regular expression to exclude files")
    args = parser.parse_args()

    register_folder(args.folder_path)
