# Knowledge
Data, information, and knowledge are terms that are often confused when mentioned together. Simply put, these three words have a progressively deeper relationship, with knowledge being the most abstract and requiring a high degree of stability and reliability in its content.

We all know that both traditional machine learning models and large language models require a vast amount of data during the training process, and we always hope that this data is of high quality and reliability. Although many existing large language models already include an impressive collection of data and instructions, similar to how no human can become omniscient and omnipotent, these models often have "knowledge" blind spots.

By loading additional knowledge content, agents can learn and master parts of the knowledge that their original LLMs are not proficient in. Just like humans learn knowledge, agents can make themselves more knowledgeable through this method.

agentUniverse defines a standard knowledge format, which includes various knowledge data loading methods, and connections to diverse knowledge storage systems. You can define any form of knowledge data into standard knowledge components for agents and other components to use.

## Knowledge Structure

In agentUniverse, the overall architecture of Knowledge and its related domain objects is illustrated in the following diagram:
![agentUniverse Knowledge architecture](../../../../_picture/knowledge_structure.png)
The upper part of the diagram, from Reader to Store, represents the Knowledge injection process, while the lower part represents the Knowledge query process.

### Knowledge Injection Process

In the Knowledge injection process, `Reader` is used to read raw data and convert it into the `Document` format used within agentUniverse. A Document can contain various types of content such as text, images, vectors, etc., and can be extended to include more forms such as audio or video by inheriting this type. After that, the `DocProcessor` performs a series of processing operations on the `Document`. As shown in the diagram, the input and output of the `DocProcessor` are both in the form of a `Document`, meaning you can stack multiple `DocProcessors` during this process. Finally, the processed `Document` is stored in different Stores, which can be any type of data storage, including but not limited to relational databases, vector databases, and graph databases. Therefore, the same Document can be stored in different Stores in various forms, but they will share the same ID in their metadata, indicating that they originate from the same Document. This is used to avoid retrieving duplicate content during subsequent queries.

### Knowledge Query Process
When querying Knowledge, the user needs to construct a `Query`. Like `Document`, the content of a Query can also be diverse, ranging from simple strings to vectors or images——as long as the Store containing the Knowledge supports that query format. After passing the Query into the Knowledge component, similar to `DocProcessor`, the `QueryParaphraser` is used to process the Query. You can extract keywords from the original query string to query paragraphs with specific tags, or split the original query into multiple sub-queries that are easier to search, among other possibilities. After that, the RagRouter component is responsible for pairing the Query with the appropriate `Store`, generating multiple [Query, Store] query tasks. This pairing can be based on the LLM's understanding of the match between the query text and the Store descriptions, or it can be based on specific rules to select certain Stores. If resources allow, queries can even be performed on all Stores directly. The content returned from `Store` queries is still in the Document format, so we can continue to use `DocProcessor` for a series of post-processing tasks on the retrieved Documents. The difference here is that the `Query` will also be passed as a default parameter to the `DocProcessor`, allowing for processing tasks like reranking that require comparing the retrieved content with the `Query`. Finally, you can convert the retrieved Documents into a string format that is more understandable by the LLM using the default or custom to_llm method, which serves as the final output.

### Recall query ownership

Each routed task receives a deep copy of its `Query` before any store is dispatched.
A store may derive its own keywords or modify nested query fields without affecting
another store or the query passed to post-processors. This matters, for example,
when SQLite stores use different keyword extractors. Router task order, store codes
and result deduplication/fusion are unchanged.

All routed queries must be deep-copyable. A custom payload that cannot be copied
raises before dispatch instead of falling back to unsafe shared state. Copying
vectors/images adds memory proportional to the routed payloads; routers should
bound fan-out. This isolates query data, not store clients/connections or returned
documents, and does not synchronize external mutations by custom router threads.

# Conclusion
By now, you should have a basic understanding of the design principles behind knowledge components. In the next section, we will introduce you to the standard definitions of knowledge components, how to customize and create your own knowledge, and how to utilize knowledge.
