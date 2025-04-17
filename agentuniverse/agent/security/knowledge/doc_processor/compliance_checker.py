from typing import List, Dict, Optional
import re
from collections import defaultdict

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager

class ComplianceDocProcessor(DocProcessor):
    def process_docs(self, docs: List[Document], query: Optional[Query] = None) -> List[Document]:
        """处理文档流程：
        1. 加载合规规则
        2. 评估每个文档风险
        3. 根据阈值过滤文档
        """
        rules = self._load_compliance_rules()
        risk_threshold = query.metadata.get('risk_threshold', 0.7) if query else 0.7

        safe_docs = []
        for doc in docs:
            risk_score = self._assess_risk(doc.text, rules, query)
            doc.metadata.update({
                'risk_score': risk_score,
                'risk_level': self._get_risk_level(risk_score)
            })

            if risk_score < risk_threshold:
                safe_docs.append(doc)

        return safe_docs

    def _load_compliance_rules(self) -> Dict:
        """从合规知识库加载规则"""
        store: Store = StoreManager().get_instance('compliance_rules_store')
        return {
            rule.metadata['pattern_type']: {
                'patterns': rule.text.split('|'),
                'weight': rule.metadata['weight']
            }
            for rule in store.get_all_documents()
        }

    def _assess_risk(self, text: str, rules: Dict, query: Query) -> float:
        """风险评估逻辑"""
        risk_score = 0
        matched_rules = defaultdict(list)

        # 关键词匹配
        for keyword in rules.get('keyword', {}).get('patterns', []):
            if re.search(rf'\b{keyword}\b', text, flags=re.IGNORECASE):
                matched_rules['keywords'].append(keyword)
                risk_score += rules['keyword']['weight']

        # 正则表达式匹配
        for pattern in rules.get('regex', {}).get('patterns', []):
            if re.search(pattern, text):
                matched_rules['regex'].append(pattern)
                risk_score += rules['regex']['weight']

        # 上下文规则（示例）
        if 'sensitive_context' in rules:
            if self._detect_sensitive_context(text):
                risk_score += rules['sensitive_context']['weight']

        return min(risk_score, 1.0)  # 确保不超过1

    def _get_risk_level(self, score: float) -> str:
        """风险等级划分"""
        if score >= 0.8: return '高危'
        if score >= 0.5: return '中危'
        return '低危'

    def _detect_sensitive_context(self, text: str) -> bool:
        """使用NLP模型检测敏感上下文"""
        # 可替换为实际模型调用
        sensitive_triggers = ['群体事件', '政治运动', '意识形态']
        return any(trigger in text for trigger in sensitive_triggers)