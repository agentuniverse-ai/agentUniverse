# RAG

Retrieval-Augmented Generation (RAG) is a cutting-edge natural language processing (NLP) technique that significantly enhances the accuracy and diversity of text generation tasks by combining information retrieval and generative models. The core idea of RAG is to first retrieve the most relevant content from a large document corpus based on the input query and then pass this retrieved information as context to the generative model. This allows the generative model to not only rely on its training data but also dynamically access up-to-date external knowledge, enabling the agent to generate responses that are more contextually appropriate.

## General RAG Workflow
![rag_structure](../../../_picture/rag_structure.png)

According to [this review](https://arxiv.org/pdf/2312.10997), the majority of current RAG workflows can be summarized into three parts:

1. Document Index Construction: This involves transforming the documents from a large-scale corpus into a form that is easy to retrieve, usually by splitting the text into smaller chunks and converting them into vector embeddings stored in a vector database.
2. Retrieval of Relevant Knowledge: After a user provides a query, the system retrieves a set of relevant documents from the index constructed in the first step. This process may include query reformulation (to ensure the query retrieves more relevant content), re-ranking of documents (to select the most relevant subset from a large number of retrieved items), and other steps—all aimed at filtering out the documents most relevant to the original query.
3. Final Response Generation: In this step, the documents retrieved in the second step are fed into a large model, which, combined with the prompt and original query, generates the final response.

## RAG in agentUniverse
In contrast to the general RAG workflow described above, agentUniverse breaks down RAG into two parts:

1. Knowledge Component: This includes the ability to build a knowledge base from documents and retrieve knowledge based on a query. You can refer to [Knowledge](../../In-Depth_Guides/Tutorials/Knowledge/Knowledge.md) for detailed usage instructions.
2. Agent-Driven Response Generation Using Knowledge: Once the knowledge component is built in the first step, the agent can use it to retrieve documents relevant to the query and then pass these, along with the prompt and context, to a large model to generate the final response. For specific usage methods, you can refer to [Agent Creation and Use ](../../In-Depth_Guides/Tutorials/Agent/Agent_Create_And_Use.md) and set any knowledge you’ve created under the agent's action knowledge section.

If you want to quickly build a RAG workflow using your own documents and use it in an agent, you can refer to [How to Build Knowledge Base](../../How-to/Build%20and%20Use%20a%20Knowledge%20Base/How_to_Build_Knowledge_Base.md) and [How to Use Knowledge Base](../../How-to/Build%20and%20Use%20a%20Knowledge%20Base/How_to_Use_Knowledge_Base.md).
