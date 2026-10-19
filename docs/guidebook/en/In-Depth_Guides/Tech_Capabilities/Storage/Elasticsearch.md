## Elasticsearch
If you wish to utilize the Elasticsearch vector database within agentUniverse, you need to follow these steps:

1. Install the Elasticsearch vector database
You can consult the [official Elasticsearch installation documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html) for detailed instructions. As a recommendation, you can start the Elasticsearch container in Docker by executing the following commands:

``` shell
$ docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.15.0
```
The container serves the REST API on port 9200 with security disabled for a quick start; for production deployments refer to the official documentation. The dense_vector field with kNN search requires Elasticsearch 8.x or above.

2. Install the Elasticsearch Python SDK
```
pip install elasticsearch
```

### How to Configure Elasticsearch Components
```yaml
name: 'elasticsearch_store'
description: 'a store based on elasticsearch'
index_name: 'agentuniverse'
distance: 'COSINE'
similarity_top_k: 10
with_vectors: false
connection_args:
  hosts: 'http://localhost:9200'
  # api_key: 'your-elasticsearch-api-key'
  # basic_auth: ['elastic', 'your-password']
embedding_model: 'openai_embedding'
metadata:
  type: 'STORE'
  module: 'agentuniverse.agent.action.knowledge.store.elasticsearch_store'
  class: 'ElasticsearchStore'
```
- connection_args: Arguments passed to the `elasticsearch.Elasticsearch` client, e.g. hosts, api_key, basic_auth, cloud_id.
- index_name: The Elasticsearch index that stores the documents; it is created automatically with a dense_vector mapping on first insert.
- distance: The dense_vector similarity metric, one of COSINE (default), EUCLID, DOT.
- num_candidates: The kNN num_candidates parameter; defaults to 10 x similarity_top_k as recommended by Elasticsearch.
- with_vectors: If true, query results also carry the stored vectors.
- embedding_model: The model employed to generate embedding vectors, for example openai_embedding.
- similarity_top_k: The number of the most similar results returned in a similarity search.

### Usage
[Knowledge_Define_And_Use](../../../In-Depth_Guides/Tutorials/Knowledge/Knowledge_Define_And_Use.md)
