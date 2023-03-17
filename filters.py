#!/User/ricardo/anaconda3/bin/python
# -*- encoding: utf-8 -*-
"""
@File     :  filters.py
@Time     :  2023/03/17 20:47:32
@Author   :  Ricardo
@Version  :  1.0
@Desc     :  Custom Jinja2 filters
"""

# import lib here


def datetime_format(value, format_="%Y-%m-%d %H:%M:%S"):
    return value.strftime(format_)


def format_size(size: int):
    if size < 1024:
        return f"{size}Bytes"
    if size < 1024**2:
        return f"{size / 1024:.2f}KB"
    if size < 1024**3:
        return f"{size / 1024 ** 2:.2f}MB"
    return f"{size / 1024 ** 3:.2f}GB"
