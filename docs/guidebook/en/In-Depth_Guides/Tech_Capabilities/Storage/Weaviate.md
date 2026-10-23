## Weaviate
If you wish to utilize the Weaviate vector database within agentUniverse, you need to follow these steps:

1. Install the Weaviate vector database
You can consult the [official Weaviate installation documentation](https://weaviate.io/developers/weaviate/installation) for detailed instructions on installing and using Weaviate. As a recommendation, you can start the Weaviate container in Docker by executing the following commands:

``` shell
$ docker run -d --name weaviate \
  -p 8080:8080 -p 50051:50051 \
  -e AUTHENTICATION_APIKEY_ENABLED='true' \
  -e AUTHENTICATION_APIKEY_ALLOWED_KEYS='your-weaviate-api-key' \
  -e AUTHENTICATION_APIKEY_USERS='admin@weaviate.io' \
  -e AUTHORIZATION_ADMINREAD_ENABLED='true' \
  cr.weaviate.io/semitechnologies/weaviate:latest
```
These commands will download the Weaviate image and start a container that serves the REST API on port 8080 and the gRPC API on port 50051. For additional information and alternative installation methods, kindly refer to the official documentation.

2. Install the Weaviate Python SDK
```
pip install weaviate-client
```

### How to Configure Weaviate Components
```yaml
name: 'weaviate_store'
description: 'a store based on weaviate'
collection_name: 'agentuniverse'
distance: 'COSINE'
similarity_top_k: 10
with_vectors: false
connection_args:
  http_host: 'localhost'
  http_port: 8080
  http_secure: false
  grpc_host: 'localhost'
  grpc_port: 50051
  grpc_secure: false
api_key: 'your-weaviate-api-key'
embedding_model: 'openai_embedding'
metadata:
  type: 'STORE'
  module: 'agentuniverse.agent.action.knowledge.store.weaviate_store'
  class: 'WeaviateStore'
```
- connection_args: Parameters required for connecting to the Weaviate server through the v4 client: http_host, http_port, http_secure, grpc_host, grpc_port, grpc_secure.
- api_key: The API key credential when the server has API key authentication enabled; remove it for servers without authentication.
- collection_name: The Weaviate collection that stores the documents; it is created automatically with the configured distance metric on first insert.
- distance: The vector distance metric used for the collection index, one of COSINE (default), EUCLID, DOT, MANHATTAN, HAMMING.
- with_vectors: If true, query results also carry the stored vectors.
- embedding_model: The model employed to generate embedding vectors, for example openai_embedding.
- similarity_top_k: The number of the most similar results returned in a similarity search.

### Usage
[Knowledge_Define_And_Use](../../../In-Depth_Guides/Tutorials/Knowledge/Knowledge_Define_And_Use.md)
