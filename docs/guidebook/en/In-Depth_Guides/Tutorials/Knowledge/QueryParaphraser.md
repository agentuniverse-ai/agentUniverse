# QueryParaphraser

The QueryParaphraser is responsible for processing and refining the original Query, including rewriting, splitting, and keyword extraction. This allows the Query to retrieve more accurate and richer content from the Store. The input and output of the QueryParaphraser are both in the form of a Query, enabling the Query to undergo multiple layers of paraphrasing.


The Query is defined as follows:
```python
from PIL.Image import Image
from typing import Optional, List, Set

from pydantic import BaseModel, Field


class Query(BaseModel):
    query_str: Optional[str] = None
    query_text_bundles: Optional[List[str]] = Field(default_factory=list)
    query_image_bundles: Optional[List[Image]] = Field(default_factory=list)
    keywords: Optional[Set[str]] = Field(default_factory=set)
    embeddings: List[List[float]] = Field(default_factory=list)
    ext_info: dict = {}
    similarity_top_k: Optional[int] = None
```
- query_str: An optional string field used to store the text content of the original query.
- query_text_bundles: An optional list of strings used to store multiple rewritten query text segments.
- query_image_bundles: An optional list of images used to store multiple query images.
- keywords: An optional set field used to store the keywords of the query.
- embeddings: A list of embedding vectors used to store the query's embedding representations for similarity matching.
- ext_info: A dictionary field used to store additional information related to the query, supporting arbitrary extensions.
- similarity_top_k: An optional integer field used to specify the number of most similar results to return in similarity searches.

The QueryParaphraser is defined as follows:
```python
from abc import abstractmethod
from typing import Optional

from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.component.component_base import ComponentBase


class QueryParaphraser(ComponentBase):

    component_type: ComponentEnum = ComponentEnum.QUERY_PARAPHRASER
    name: Optional[str] = None
    description: Optional[str] = None

    @abstractmethod
    def query_paraphrase(self, origin_query: Query) -> Query:
        """Paraphrase the origin query string to different style."""
```
When creating a custom subclass of QueryParaphraser, you need to override the query_paraphrase method, with both the input and output in the form of a Query.

After writing the corresponding code, you can refer to the following YAML configuration to register the QueryParaphraser as an aU component:
```yaml
name: 'query_keyword_extractor'
description: 'extract keywords from query origin str'
metadata:
  type: 'QUERY_PARAPHRASER'
  module: 'agentuniverse.agent.action.knowledge.query_paraphraser.query_keyword_extractor'
  class: 'QueryKeywordExtractor'
```
The type in the metadata must be QUERY_PARAPHRASER。
### Pay Attention to the Package Path of Your Custom QueryParaphrase:

In the config.toml file of the agentUniverse project, you need to configure the package path corresponding to your QueryParaphraser. Please double-check whether the path of the file you created is under the query_paraphraser path or its subdirectories in CORE_PACKAGE.

For example, the configuration in the sample project is as follows:
```yaml
[CORE_PACKAGE]
query_paraphraser = ['sample_standard_app.intelligence.agentic.knowledge.query_paraphraser']
```

## The following QueryParaphraser are built into agentUniverse:
### [query_keyword_extractor](../../../../../../agentuniverse/agent/action/knowledge/query_paraphraser/query_keyword_extractor.yaml)
This component extracts keywords from the original text in the Query and saves them into the keywords field of the Query.
The component definition file is as follows:
```yaml
name: 'query_keyword_extractor'
description: 'extract keywords from query origin str'
metadata:
  type: 'QUERY_PARAPHRASER'
  module: 'agentuniverse.agent.action.knowledge.query_paraphraser.query_keyword_extractor'
  class: 'QueryKeywordExtractor'
```

### [hyde_query_paraphraser](../../../../../../agentuniverse/agent/action/knowledge/query_paraphraser/hyde_query_paraphraser.yaml)
This component implements HyDE (Hypothetical Document Embeddings) query expansion: it asks a registered LLM component to write one or more short *hypothetical passages* that would answer the user query, and rewrites the Query with them, so dense retrieval matches "answer-shaped" text instead of a bare question (closing the query-vs-document asymmetry).

The rewrite follows the framework Query contract: `query_str` is rewritten (`append` mode = original query followed by the passages, the default hybrid form; `replace` mode = passages only, the classical HyDE form); every passage is also appended to `query_text_bundles`, and the untouched original query plus the generated passages are recorded under the `ext_info` keys `hyde_origin_query_str` / `hyde_documents` for later stages (fusion, rerankers, logging).

Expansion is best-effort by design: an empty query, an unset `llm_model`, a failing LLM call, or an empty generation degrades to pass-through with a logged warning — retrieval never breaks because the enhancement failed. Configuration errors instead fail loudly at component-load time (unknown `mode`, `num_docs` outside [1, 5], non-positive `max_doc_chars`, or a custom `prompt_template` without the literal `{query}` placeholder).

Generation is bounded: `num_docs` passages (1-5) with one LLM call each, every passage truncated to `max_doc_chars`, and duplicates removed. The LLM output is treated strictly as retrieval text — it is never executed or parsed as structured data.

The component definition file is as follows:
```yaml
name: 'hyde_query_paraphraser'
description: 'HyDE query expansion with LLM-generated hypothetical passages'
llm_model: ''            # registered LLM component, e.g. 'default_openai_llm'
num_docs: 1              # passages to generate, in [1, 5]
mode: 'append'           # append (original + passages) | replace (classical HyDE)
max_doc_chars: 2000      # hard truncation bound per passage
origin_query_key: 'hyde_origin_query_str'
documents_key: 'hyde_documents'
metadata:
  type: 'QUERY_PARAPHRASER'
  module: 'agentuniverse.agent.action.knowledge.query_paraphraser.hyde_query_paraphraser'
  class: 'HyDEQueryParaphraser'
```
- llm_model: name of the registered LLM component used to generate the passages. When empty, queries pass through unchanged (with a warning), so the shipped definition loads without any model credentials.
- num_docs: number of hypothetical passages to generate, in [1, 5]; one LLM call per passage, duplicates removed.
- mode: `append` (default) rewrites `query_str` to the original query followed by the passages; `replace` keeps the passages only (classical HyDE).
- max_doc_chars: hard truncation bound applied to every passage before it can reach the query or an embedding model.
- prompt_template: custom user-prompt template; must contain the literal `{query}` placeholder (substituted via `str.replace`, so other braces are safe). Defaults to a built-in instruction that answers in the language of the query.
- origin_query_key / documents_key: the `ext_info` keys recording the untouched original query string and the generated passage list.
