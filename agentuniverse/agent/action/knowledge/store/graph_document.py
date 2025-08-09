# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/22 18:16
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: graph_document.py
from .document import Document

try:
    import pandas as pd
except ImportError:
    raise ImportError(
        "The functionality you are trying to use requires the pandas and pandas package. "
        "You can install it by running: pip install pandas"
    )


class GraphDocument(Document):
    """The basic class for an ImageDocument.

    Attributes:
        graph_data: A pandas dataframe contents all results of neo4j cypher
    """
    graph_data: pd.DataFrame = None
