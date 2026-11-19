# AWS Bedrock

`AWSBedrockLLM` 和 `AWSBedrockEmbedding` 使用可选的 Boto3 SDK。
导入或创建组件不需要 SDK，首次创建 AWS 客户端时才需要。

## 安装

在包含此 extra 的源码目录中，使用隔离环境安装：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[aws_ext]'
```

已发布且包含此 extra 的版本可使用 `python -m pip install 'agentUniverse[aws_ext]'`。
该选项声明 `boto3>=1.34.131,<2.0.0`，由 Boto3 安装匹配的 Botocore，提供
Bedrock Runtime 的 `converse` / `converse_stream` API。
普通安装不会通过这条依赖声明安装 Boto3。

此 extra **不包含** `langchain-aws`。LLM 的 `as_langchain()` 需要额外安装与项目固定
LangChain 依赖兼容的版本，原生 `call`/`acall` 不需要它。
Embedding 适配器使用已有的 `langchain-community`，并需要 Boto3。

## 配置

设置 `AWS_REGION`（默认 `us-east-1`），并通过
[AWS 凭据提供链](https://docs.aws.amazon.com/boto3/latest/guide/credentials.html)
配置 IAM Role 或 AWS Profile，也支持 `AWS_ACCESS_KEY_ID` 和 `AWS_SECRET_ACCESS_KEY`。
LLM 额外提供 `aws_session_token` / `AWS_SESSION_TOKEN`。Embedding 使用临时凭据时，
请使用 Profile、Role，或注入使用完整凭据创建的客户端，不要只传 access key 和 secret。
不要将凭据提交到代码或配置中。

内置配置为 `agentuniverse/llm/default/aws_bedrock_llm.yaml` 和
`agentuniverse/agent/action/knowledge/embedding/aws_bedrock_embedding.yaml`。
选择当前账户和区域可用的模型，例如：

```python
from agentuniverse.agent.action.knowledge.embedding.aws_bedrock_embedding import AWSBedrockEmbedding

embedding = AWSBedrockEmbedding(
    embedding_model_name="amazon.titan-embed-text-v2:0",
    aws_region="us-east-1",
    dimensions=1024,
)
vectors = embedding.get_embeddings(["A research question"])
```

该示例会将文本发送到 AWS，可能产生费用。

## 离线测试契约

安装基础依赖及 pytest 后，在仓库根目录运行：

```bash
python -m pytest -q \
  tests/test_agentuniverse/unit/llm/test_aws_bedrock*.py \
  tests/test_agentuniverse/unit/agent/action/knowledge/embedding/test_aws_bedrock*.py
```

离线测试注入模拟客户端，并模拟 SDK 未安装。无论是否安装 `aws_ext`，测试都应在
不提供凭据、不访问网络的情况下通过。LangChain 适配器单元测试只检查构造参数，
不调用远端服务。Embedding mock 测试中重复的真实 API 用例已移除。

真实测试默认跳过，仅在**安装 Boto3 且显式设置开关**时运行：

```bash
AGENTUNIVERSE_RUN_AWS_TESTS=1 python -m pytest -q \
  tests/test_agentuniverse/unit/llm/test_aws_bedrock_llm.py \
  tests/test_agentuniverse/unit/agent/action/knowledge/embedding/test_aws_bedrock_embedding.py
```

真实测试使用你的 AWS 凭据，可能产生费用。可通过 `AWS_BEDROCK_TEST_LLM_MODEL`
覆盖 LLM 模型；Embedding 测试使用文件中的 Titan/Cohere 模型 ID，请确认区域支持。
显式启用且安装 SDK 后，凭据、权限、网络或断言错误都会报告为失败，不再静默跳过。
