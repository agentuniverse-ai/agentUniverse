# How to Define the Knowledge Component
Based on the design features of agentUniverse domain components, creating a knowledge definition involves two parts:

* knowledge_xx.yaml
* knowledge_xx.py

The `knowledge_xx.yaml` file contains important information about the knowledge component such as its name, description, loading method, storage method, etc., while the `knowledge_xx.py` file contains the specific definitions of the knowledge. Understanding this principle, let's delve into how to create these two parts.

## Creating the Knowledge Configuration - knowledge_xx.yaml
### An Example of a Knowledge Definition Configuration
```yaml
name: "sample_knowledge"
description: "a knowledge sample"
stores:
    - "a_store"
    - "another_store"
query_paraphrasers:
    - "a_query_paraphraser"
insert_processors:
    - "a_doc_processor"
rag_router: "a_rag_router"
post_processors:
    - "another_doc_processor"
readers:
    pdf: "default_pdf_reader"
metadata:
  type: 'KNOWLEDGE'
  module: 'sample_standard_app.intelligence.agentic.knowledge.sample_knowledge'
  class: 'SampleKnowledge'
```
- stores: All associated Stores. A list of strings, where each string represents the name of a Store component.
- query_paraphrasers: Query paraphrasers that convert the input query into a form more suitable for retrieval. A list of strings, where each string represents the name of a QueryParaphraser component.
- insert_processors: Insert processors that process text when inserting it into the knowledge base, such as recursive character splitting. A list of strings, where each string represents the name of a DocProcessor component.
- rag_router: The Retrieval-Augmented Generation (RAG) router that controls how queries are routed within the knowledge base.
- post_processors: Post-processors that optimize and rank retrieval results to enhance the relevance of the returned results. A list of strings, where each string represents the name of a DocProcessor component.
- readers: A dictionary where the key represents the file type, and the value represents the corresponding `Reader` component's name.

## Creating Knowledge Domain Behavior Definition - knowledge_xx.py
agentUniverse provides a standard Knowledge class that you can use directly in the YAML definition file or extend by overriding some of its methods.

### [Knowledge Class Definition:](../../../../../../agentuniverse/agent/action/knowledge/knowledge.py)

- _load_data(self, *args: Any, **kwargs: Any) -> List[Document]
: Loads the data source and selects an appropriate reader based on the type of data source (file or URL) to load the document data.

- _insert_process(self, origin_docs: List[Document]) -> List[Document]
: Processes the original documents to be inserted by sequentially applying the configured document processors for preprocessing.

- _rag_post_process(self, origin_docs: List[Document], query: Query)
: Post-processes the retrieved original documents by applying the configured post-processors based on the query conditions.

- _paraphrase_query(self, origin_query: Query) -> Query
: Rewrites the original query by applying the configured query paraphrasers.

- insert_knowledge(self, **kwargs) -> None
: Inserts knowledge data. This method calls `_load_data` to load document data, preprocesses the documents through `_insert_process`, and then inserts the documents into the storage in parallel.

- _route_rag(self, query: Query)
: Routes the query to the appropriate storage using the specified RAG router based on the query conditions.

- query_knowledge(self, **kwargs) -> List[Document]
: Queries knowledge data. This method first rewrites the query by calling `_paraphrase_query`, then routes it to storage via `_route_rag`, performs the query in parallel, and finally post-processes the query results via `_rag_post_process`.

- to_llm(self, retrieved_docs: List[Document]) -> Any
: Converts the retrieved documents into a format suitable for input to a Large Language Model (LLM), concatenating all document texts for further processing.


## Pay Attention to the Package Path of Your Defined Knowledge
With the above Knowledge configuration and definition, you have mastered all the steps required to create Knowledge. Next, before using these Knowledge components, ensure that they are in the correct package scan path.

In the config.toml file of the agentUniverse project, you need to configure the package path for the Knowledge component. Ensure that the package path of the file you created is under the `CORE_PACKAGE` in the `knowledge` path or its subpaths.

For example, in the configuration of the sample project:
```yaml
[CORE_PACKAGE]
# Scan and register knowledge components for all paths under this list, with priority over the default.
knowledge = ['sample_standard_app.intelligence.agentic.knowledge']
```

# How to Use the Knowledge Component
## Configuring Knowledge in an Agent
Based on the content in [Creating and Using Agents](../../../In-Depth_Guides/Tutorials/Agent/Agent_Create_And_Use.md), you can set any created knowledge under the knowledge action in the agent.

## Ollama embedding batch lifecycle

`OllamaEmbedding.async_get_embeddings` runs requests concurrently and returns vectors in input order. If one request fails or is cancelled, unfinished requests in that batch are cancelled and awaited before the operation exits. Caller cancellation is propagated as cancellation, not converted into a normal result. Shared HTTP clients and unrelated tasks are not closed or cancelled. Cleanup relies on requests cooperating with asyncio cancellation; it cannot undo computation already performed by the server and does not add automatic retries or a concurrency limit.

## Using the Knowledge Manager
You can obtain the Knowledge instance corresponding to the name via the `.get_instance_obj(xx_knowledge_name)` method in the Knowledge Manager, and call it using the `query_knowledge` method.

```python
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager

knowledge = KnowledgeManager().get_instance_obj("knowledge_name")
knowledge.insert_knowledge(source_path="source_file")
knowledge.query_knowledge()
```

## Learn More About Existing Knowledge
[Legal Consultation Case](../../../Examples/Legal_Advice.md)
