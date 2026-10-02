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

### [multi_query_paraphraser](../../../../../../agentuniverse/agent/action/knowledge/query_paraphraser/multi_query_paraphraser.yaml)
This component implements multi-query expansion: a single LLM call generates several *reformulations* of the original question (same intent, varied wording), and the Query is rewritten with them, so dense retrieval also covers corpus passages that phrase the intent differently. It is the question-side counterpart of HyDE-style expansion (which generates answer-shaped passages); the two compose naturally in a `query_paraphrasers` chain.

The rewrite follows the framework Query contract: variants are appended to `query_text_bundles`; `query_str` is rewritten (`append` mode = original query followed by the variants, the default; `replace` mode = variants only); and the untouched original plus the final variant list are recorded under the `ext_info` keys `multi_query_origin_query_str` / `multi_query_variants` for later stages (fusion, rerankers, logging).

The output parser tolerates the usual LLM decoration (`1.` / `1)` / `1、` numbering, `-`/`*`/`•` bullets, wrapping quotes), drops empty lines, variants equal to the original query (whitespace-folded, case-insensitive) and duplicates, caps the list at `num_queries`, and truncates each variant to `max_query_chars`.

Expansion is best-effort by design: an empty query, an unset `llm_model`, a failing LLM call, or output without any usable variant degrades to pass-through with a logged warning — retrieval never breaks because the enhancement failed. Configuration errors instead fail loudly at component-load time (unknown `mode`, `num_queries` outside [1, 10], non-positive `max_query_chars`, or a custom `prompt_template` without the literal `{query}` placeholder).

The component definition file is as follows:
```yaml
name: 'multi_query_paraphraser'
description: 'expand the query with LLM-generated reformulations'
llm_model: ''            # registered LLM component, e.g. 'default_openai_llm'
num_queries: 3           # variants to keep, in [1, 10]; one LLM call
mode: 'append'           # append (original + variants) | replace
max_query_chars: 512     # hard truncation per variant
origin_query_key: 'multi_query_origin_query_str'
variants_key: 'multi_query_variants'
metadata:
  type: 'QUERY_PARAPHRASER'
  module: 'agentuniverse.agent.action.knowledge.query_paraphraser.multi_query_paraphraser'
  class: 'MultiQueryParaphraser'
```
- llm_model: name of the registered LLM component used to generate the variants. When empty, queries pass through unchanged (with a warning), so the shipped definition loads without any model credentials.
- num_queries: maximum number of variants to keep, in [1, 10]; the LLM is asked for exactly this many in one call.
- mode: `append` (default) rewrites `query_str` to the original query followed by the variants; `replace` keeps the variants only.
- max_query_chars: hard truncation bound applied to every variant.
- prompt_template: custom user-prompt template; must contain the literal `{query}` placeholder and may contain `{num}` (replaced first, so other braces are safe). Defaults to a built-in instruction that answers in the language of the query.
- origin_query_key / variants_key: the `ext_info` keys recording the untouched original query string and the final variant list.