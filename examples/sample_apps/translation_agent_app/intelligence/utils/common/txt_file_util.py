# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/1 16:05
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: txt_file_util.py
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class TxtFileOps(object):
    def __init__(self):
        return

    @classmethod
    def is_file_exist(cls, file_path):
        file_name, ext = os.path.splitext(file_path)
        if ext.lower() != '.txt':
            raise Exception('Unsupported file extension')
        return os.path.exists(file_path)


class TxtFileReader(object):

    def __init__(self, file_path: str):
        self.file_handler = None
        self.file_name = file_path
        if TxtFileOps.is_file_exist(file_path):
            self.file_handler = open(file_path, 'r', encoding='utf-8')

    def read_txt_obj(self):
        if not self.file_handler:
            raise Exception(f"No txt file to read: {self.file_name}")
        txt_line = self.file_handler.readline()
        if txt_line:
            return txt_line.strip()
        else:
            return None

    def read_txt_obj_list(self):
        obj_list = []
        while True:
            obj = self.read_txt_obj()
            if obj is None:
                break
            obj_list.append(obj)
        return obj_list
