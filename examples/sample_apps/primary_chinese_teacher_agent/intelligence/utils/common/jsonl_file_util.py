# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/1 21:09
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: jsonl_file_util.py
import json
import os
import sys

from agentuniverse.base.util.logging.logging_util import LOGGER

DATA_DIR = './data/'

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class JsonFileOps(object):
    def __init__(self):
        return

    @classmethod
    def is_file_exist(cls, file_path):
        file_name, ext = os.path.splitext(file_path)
        if ext.lower() != '.jsonl':
            raise Exception('Unsupported file extension')
        return os.path.exists(file_path)


class JsonFileReader(object):
    def __init__(self, file_path: str):
        self.file_handler = None
        self.file_name = file_path
        if JsonFileOps.is_file_exist(file_path):
            self.file_handler = open(file_path, 'r', encoding='utf-8')

    def read_json_obj(self):
        if not self.file_handler:
            raise Exception(f"None json file to read: {self.file_name}")
        json_line = self.file_handler.readline()
        if json_line:
            try:
                json_obj = json.loads(json_line.strip())
                return json_obj
            except Exception as e:
                LOGGER.warn(f"except[read_json_line]>>>{e}:{json_line}")
                return json.loads('{}')
        else:
            return None

    def read_json_obj_list(self):
        obj_list = []
        while True:
            obj = self.read_json_obj()
            if obj is None:
                break
            obj_list.append(obj)
        return obj_list


class JsonFileWriter(object):
    def __init__(self, output_file_name: str, extension='jsonl', directory=DATA_DIR):
        self.outfile_path = directory + output_file_name + '.' + extension
        directory = os.path.dirname(self.outfile_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.outfile_handler = open(self.outfile_path, 'w', encoding='utf-8')

    def write_json_obj(self, json_obj: dict):
        try:
            # confirm that it's a json string and then write.
            json_line = json.dumps(json_obj, ensure_ascii=False)
            self.outfile_handler.write(json_line.strip() + '\n')
            self.outfile_handler.flush()
        except Exception as e:
            LOGGER.warn(f"except[write_json_obj]>>>{e}:{json_obj}")
        return

    def write_json_obj_list(self, json_obj_list: list):
        for i in range(0, len(json_obj_list)):
            self.write_json_obj(json_obj_list[i])
        return

    def write_json_query_answer(self, query: str, answer: str):
        json_obj = {"query": query, "answer": answer}
        self.write_json_obj(json_obj)

    def write_json_query_answer_list(self, query_answer_list: list):
        for i in range(0, len(query_answer_list)):
            self.write_json_query_answer(query_answer_list[i][0], query_answer_list[i][1])
