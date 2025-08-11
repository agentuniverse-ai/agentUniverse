# database.py
import sqlite3
import os
from flask import g

# 假设当前文件在 backend 目录下，db 文件在同一级目录
DB_PATH = os.path.join(os.path.dirname(__file__), 'sqlite_memory.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row  # 支持字典式访问
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()