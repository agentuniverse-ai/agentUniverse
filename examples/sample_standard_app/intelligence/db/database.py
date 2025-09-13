# intelligence/db/database.py
import sqlite3
import os
from flask import g

DB_PATH = os.path.join(os.path.dirname(__file__), 'agent_universe.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with db:
        db.execute('''
        CREATE TABLE IF NOT EXISTS request_task (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT NOT NULL,
            query TEXT,
            session_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            state TEXT DEFAULT 'finished',
            result TEXT,
            gmt_creat TEXT DEFAULT (datetime('now', 'localtime')),
            gmt_modified TEXT DEFAULT (datetime('now', 'localtime'))
        )
        ''')
        print("✅ 表 'request_task' 已确保存在")

def init_app(app):
    """
    将数据库生命周期管理注册到 Flask 应用
    """
    app.teardown_appcontext(close_db)

    # 替代 before_first_request：使用 before_request + 标志位
    @app.before_request
    def initialize_database():
        if not app.config.get('DB_INITIATED'):
            init_db()
            app.config['DB_INITIATED'] = True