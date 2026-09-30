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
    """Utility operations for text file handling."""

    def __init__(self):
        """Initialize the TxtFileOps instance."""
        return

    @classmethod
    def is_file_exist(cls, file_path):
        """Check whether the given text file exists.

        Args:
            file_path (str): Path of the file to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        file_name, ext = os.path.splitext(file_path)
        if ext.lower() != '.txt':
            raise Exception('Unsupported file extension')
        return os.path.exists(file_path)


class TxtFileReader(object):
    """Reader that reads non-empty lines from a text file."""

    def __init__(self, file_path: str):
        """Initialize the reader with the target text file.

        Args:
            file_path (str): Path of the .txt file to read.
        """
        self.file_handler = None
        self.file_name = file_path
        if TxtFileOps.is_file_exist(file_path):
            self.file_handler = open(file_path, 'r', encoding='utf-8')

    def read_txt_obj(self):
        """Read the next line from the file.

        Returns:
            str or None: The stripped line, or None when no line remains.
        """
        if not self.file_handler:
            raise Exception(f"No txt file to read: {self.file_name}")
        txt_line = self.file_handler.readline()
        if txt_line:
            return txt_line.strip()
        else:
            return None

    def read_txt_obj_list(self):
        """Read all remaining lines from the file.

        Returns:
            list: All remaining lines, stripped of surrounding whitespace.
        """
        obj_list = []
        while True:
            obj = self.read_txt_obj()
            if obj is None:
                break
            obj_list.append(obj)
        return obj_list
