# Authenticated Ollama embeddings through LangChain

`OllamaEmbedding.as_langchain()` preserves the configured service URL, model
and `ollama_api_key`. A nonempty key is sent as `Authorization: Bearer ...`
by LangChain document/query requests, including its asynchronous interfaces.
Without a key, requests continue to omit the authorization header.

```python
import os

from agentuniverse.agent.action.knowledge.embedding.ollama_embedding import OllamaEmbedding

embedding = OllamaEmbedding(
    ollama_base_url=os.environ["OLLAMA_BASE_URL"],
    ollama_api_key=os.getenv("OLLAMA_API_KEY"),
    embedding_model_name="nomic-embed-text",
)
vector = embedding.as_langchain().embed_query("Example question")
```

Conversion keeps existing component HTTP clients open. LangChain uses its own
request implementation: the declared `langchain-community==0.0.38` embedding
class has no timeout option, so the component's native HTTPX `timeout` setting
does not configure LangChain requests. Server-side authentication errors still
propagate to the caller.

## 中文说明

`OllamaEmbedding.as_langchain()` 会保留配置的服务地址、模型和 `ollama_api_key`。
非空密钥会通过 `Authorization: Bearer ...` 传给 LangChain 的文档、查询及异步
嵌入接口；未配置密钥时仍不发送认证头。上面的示例从环境变量读取配置。

转换会保留组件已有的 HTTP 客户端。LangChain 使用自己的请求实现；项目声明的
`langchain-community==0.0.38` 嵌入类没有超时选项，因此组件原生 HTTPX 的
`timeout` 设置不会控制 LangChain 请求。服务端返回的认证错误仍会向调用方抛出。
