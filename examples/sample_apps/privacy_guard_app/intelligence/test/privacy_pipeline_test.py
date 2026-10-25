# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Offline pipeline test for privacy_guard_app (no API key required).

Usage (from the app root):
    python intelligence/test/privacy_pipeline_test.py
"""

import os
import re

from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse.base.agentuniverse import AgentUniverse

APP_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAMPLE_FILE = os.path.join(
    APP_ROOT, 'intelligence', 'agentic', 'knowledge',
    'raw_knowledge_file', 'support_tickets.txt')

PII_PATTERNS = [
    r'13812345678',
    r'6222021234567894',
    r'110101199001011237',
    r'zhangwei\.customer@example\.com',
    r'EMP-100234',
    r'ORD-20240315',
]


def main():
    raw_text = open(SAMPLE_FILE, encoding='utf-8').read()
    for pattern in PII_PATTERNS:
        assert re.search(pattern, raw_text), f'sample should contain {pattern} before redaction'

    # Ensure database directory exists for clean checkouts
    db_dir = os.path.join(APP_ROOT, 'intelligence', 'db')
    os.makedirs(db_dir, exist_ok=True)

    AgentUniverse().start(
        config_path=os.path.join(APP_ROOT, 'config', 'config.toml'),
        core_mode=True)

    knowledge = KnowledgeManager().get_instance_obj('privacy_knowledge')
    assert knowledge is not None, 'privacy_knowledge failed to register'

    knowledge.insert_knowledge(source_path=SAMPLE_FILE)

    docs = knowledge.query_knowledge(query_str='退款 银行卡 到账')
    assert docs, 'query returned no documents'

    joined = '\n'.join(doc.text for doc in docs)
    for pattern in PII_PATTERNS:
        assert not re.search(pattern, joined), f'PII leaked into retrieved docs: {pattern}'
    assert '[REDACTED]' in joined, 'expected redaction placeholders in retrieved docs'
    assert any((doc.metadata or {}).get('redaction_summary') for doc in docs), \
        'expected per-document redaction_summary metadata'

    print(f'OK: {len(docs)} documents retrieved, all PII redacted.')
    print('Sample redaction summary:', docs[0].metadata.get('redaction_summary'))


if __name__ == '__main__':
    main()
