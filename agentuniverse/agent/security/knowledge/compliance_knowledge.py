import json
from typing import List, Any

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.store.document import Document


class ComplianceKnowledge(Knowledge):
    def to_llm(self, retrieved_docs: List[Document]) -> Any:

        retrieved_texts = [json.dumps({
            "text": doc.text,
            "from": doc.metadata["file_name"]
        },ensure_ascii=False) for doc in retrieved_docs]
        return '\n=========================================\n'.join(
            retrieved_texts)