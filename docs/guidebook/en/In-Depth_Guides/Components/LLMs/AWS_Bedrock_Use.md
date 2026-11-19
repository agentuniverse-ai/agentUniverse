# AWS Bedrock

`AWSBedrockLLM` and `AWSBedrockEmbedding` use the optional Boto3 SDK. Importing
or constructing a component does not need Boto3; creating an AWS client does.

## Installation

From a checkout containing the extra, use an isolated environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[aws_ext]'
```

For a published version containing the extra, use
`python -m pip install 'agentUniverse[aws_ext]'`. It declares
`boto3>=1.34.131,<2.0.0`, which supplies a matching Botocore dependency and the
Bedrock Runtime `converse` / `converse_stream` APIs. Base installations do not
install Boto3 through this dependency declaration.

The extra does **not** include `langchain-aws`. The LLM's `as_langchain()` requires
that separate package in a version compatible with the project's pinned
LangChain dependencies; native `call`/`acall` do not need it. The embedding
adapter uses the existing `langchain-community` dependency plus Boto3.

## Configuration

Set `AWS_REGION` (default `us-east-1`) and configure the
[AWS credential provider chain](https://docs.aws.amazon.com/boto3/latest/guide/credentials.html),
for example an IAM role or AWS profile. `AWS_ACCESS_KEY_ID` and
`AWS_SECRET_ACCESS_KEY` are also supported. The LLM additionally exposes
`aws_session_token` / `AWS_SESSION_TOKEN`. For temporary credentials with the
embedding component, use a profile/role or inject a client created with the full
credential set; do not supply only an access key and secret. Never commit credentials.

The built-in configurations are `agentuniverse/llm/default/aws_bedrock_llm.yaml`
and `agentuniverse/agent/action/knowledge/embedding/aws_bedrock_embedding.yaml`.
Choose a model available to your account and region. For example:

```python
from agentuniverse.agent.action.knowledge.embedding.aws_bedrock_embedding import AWSBedrockEmbedding

embedding = AWSBedrockEmbedding(
    embedding_model_name="amazon.titan-embed-text-v2:0",
    aws_region="us-east-1",
    dimensions=1024,
)
vectors = embedding.get_embeddings(["A research question"])
```

This example sends text to AWS and may incur charges.

## Offline Test Contract

With base dependencies and pytest installed, run from the repository root:

```bash
python -m pytest -q \
  tests/test_agentuniverse/unit/llm/test_aws_bedrock*.py \
  tests/test_agentuniverse/unit/agent/action/knowledge/embedding/test_aws_bedrock*.py
```

Offline tests inject fake clients and simulate missing SDK imports. They must
pass with or without `aws_ext`, credentials, or network access. The LangChain
adapter unit test checks constructor arguments, not the remote service.
Duplicate live cases have been removed from the mock embedding suite.

Live tests skip unless **both** Boto3 is installed and the opt-in flag is set:

```bash
AGENTUNIVERSE_RUN_AWS_TESTS=1 python -m pytest -q \
  tests/test_agentuniverse/unit/llm/test_aws_bedrock_llm.py \
  tests/test_agentuniverse/unit/agent/action/knowledge/embedding/test_aws_bedrock_embedding.py
```

Live tests use your credentials and may incur charges. Override the LLM model
with `AWS_BEDROCK_TEST_LLM_MODEL`; embedding tests use the Titan/Cohere model IDs
in their file. Ensure those models are available in your region. Once opted in
with the SDK installed, credential, permission, network and assertion failures
are reported as failures, not silently skipped.
