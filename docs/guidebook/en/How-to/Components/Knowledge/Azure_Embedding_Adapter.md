# Azure embedding conversion

`AzureOpenAIEmbedding.as_langchain()` preserves an explicitly configured
`embedding_model_name` as both the LangChain model and Azure deployment,
`embedding_dims` (when set), and `azure_api_version`.

The native OpenAI Azure client treats `embedding_model_name` as the deployment
name. Use the same configured deployment when passing the converted embedding
to a LangChain vector store. The API version comes from the component (including
`AZURE_API_VERSION`), rather than LangChain's separate `OPENAI_API_VERSION`
environment variable or default. If no model is configured, the adapter retains
LangChain's existing model default. Dimensions are omitted when unset.

The pinned `langchain-community==0.0.38` creates its own Azure clients during
validation, even when clients are supplied, so passing native clients alone does
not preserve configuration. Conversion retains LangChain's existing tokenization,
batching and normalization behavior; it does not promise byte-identical input
payloads or raw-vector output compared with the native API.

Run the offline request-level regressions with:

```shell
python -m pytest -q tests/test_agentuniverse/unit/agent/action/knowledge/embedding/test_azure_langchain_configuration.py
```

The tests use real pinned LangChain/OpenAI constructors and intercept HTTP sends.
Tokenizer lookup is replaced with a local deterministic encoder, avoiding model
or tokenizer downloads. No Azure account or credentials are required.
