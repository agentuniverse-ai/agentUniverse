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
    """Utility class for text file operations.

    Currently validates file extensions and checks file existence.
    """
    def __init__(self):
        """Initialize a TxtFileOps instance."""
        return

    @classmethod
    def is_file_exist(cls, file_path):
        """Check whether a '.txt' file exists at the given path.

        Args:
            file_path (str): the path of the file to check.
        Raises:
            Exception: if the file extension is not '.txt'.
        Returns:
            bool: True if the file exists, otherwise False.
        """
        file_name, ext = os.path.splitext(file_path)
        if ext.lower() != '.txt':
            raise Exception('Unsupported file extension')
        return os.path.exists(file_path)


class TxtFileReader(object):

    """Reader that reads a '.txt' file line by line.

    Opens the file in utf-8 read mode when it exists and provides
    methods to read one line or all remaining lines.
    """
    def __init__(self, file_path: str):
        """Initialize the reader with the file to read.

        Args:
            file_path (str): path of the '.txt' file to read.
        Raises:
            Exception: if the file extension is not '.txt'.
        """
        self.file_handler = None
        self.file_name = file_path
        if TxtFileOps.is_file_exist(file_path):
            self.file_handler = open(file_path, 'r', encoding='utf-8')

    def read_txt_obj(self):
        """Read the next line of the text file.

        Returns:
            str: the next line with surrounding whitespace stripped, or None
            when the end of the file is reached.
        Raises:
            Exception: if no file is open to read.
        """
        if not self.file_handler:
            raise Exception(f"No txt file to read: {self.file_name}")
        txt_line = self.file_handler.readline()
        if txt_line:
            return txt_line.strip()
        else:
            return None

    def read_txt_obj_list(self):
        """Read all remaining lines of the text file.

        Returns:
            list: the remaining lines, stripped, in file order.
        """
        obj_list = []
        while True:
            obj = self.read_txt_obj()
            if obj is None:
                break
            obj_list.append(obj)
        return obj_list
