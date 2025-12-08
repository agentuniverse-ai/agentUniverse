# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/5
# @Author  : liduowen
# @Email   : liduowen.ldw@antgroup.com
# @FileName: test_web_reader.py

import unittest
from agentuniverse.agent.action.knowledge.reader.file.web_reader import WebReader


class TestImageReader(unittest.TestCase):

    def test_page_reader(self):
        url = "https://www.baidu.com"
        reader = WebReader()
        document = reader.load_data(url)
        if document:
            print(document)


if __name__ == '__main__':
        unittest.main()