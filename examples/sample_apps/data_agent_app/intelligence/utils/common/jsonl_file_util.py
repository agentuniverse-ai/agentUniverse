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
    """Operations over .jsonl files such as checking that a file exists."""
    def __init__(self):
        """Initialize the JsonFileOps utility object."""
        return

    @classmethod
    def is_file_exist(cls, file_path):
        """Check whether file_path is an existing file with a .jsonl extension. Raises: Exception when the extension is not .jsonl. Args: file_path: The path to check. Returns: bool: True when the file exists."""
        file_name, ext = os.path.splitext(file_path)
        if ext.lower() != '.jsonl':
            raise Exception('Unsupported file extension')
        return os.path.exists(file_path)


class JsonFileReader(object):
    """Reads JSON objects from a .jsonl file, one JSON object per line."""
    def __init__(self, file_path: str):
        """Open the .jsonl file at file_path for reading when it exists. Args: file_path (str): Path of the .jsonl file to read."""
        self.file_handler = None
        self.file_name = file_path
        if JsonFileOps.is_file_exist(file_path):
            self.file_handler = open(file_path, 'r', encoding='utf-8')

    def read_json_obj(self):
        """Read and parse the next line of the file as a JSON object. Returns: The parsed object, None at end of file, or an empty dict when the line cannot be parsed (the parse error is logged)."""
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
    """Writes JSON objects to a .jsonl output file, one JSON object per line."""
    def __init__(self, output_file_name: str, extension='jsonl', directory=DATA_DIR):
        """Open the output .jsonl file at directory/output_file_name.extension for writing, creating the directory when needed. Args: output_file_name (str): Base name of the output file. extension (str): File extension, defaults to jsonl. directory (str): Output directory, defaults to DATA_DIR."""
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
