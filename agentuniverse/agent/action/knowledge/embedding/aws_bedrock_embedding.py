# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/10 14:30
# @Author  : kaichuan
# @FileName: aws_bedrock_embedding.py

import json
from typing import Any, Optional, List

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class AWSBedrockEmbedding(Embedding):
    """The AWS Bedrock embedding class.

    Supports Amazon Titan and Cohere embedding models through AWS Bedrock Runtime.

    Supported Models:
        - amazon.titan-embed-text-v1 (1536 dimensions, fixed)
        - amazon.titan-embed-text-v2 (configurable: 256, 384, 1024 dimensions)
        - cohere.embed-english-v3 (1024 dimensions)
        - cohere.embed-multilingual-v3 (1024 dimensions)

    Environment Variables:
        - AWS_ACCESS_KEY_ID: AWS access key ID
        - AWS_SECRET_ACCESS_KEY: AWS secret access key
        - AWS_REGION: AWS region (default: us-east-1)
    """

    # AWS Configuration
    aws_access_key_id: Optional[str] = Field(
        default_factory=lambda: get_from_env("AWS_ACCESS_KEY_ID"))

    aws_secret_access_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("AWS_SECRET_ACCESS_KEY"))

    aws_region: Optional[str] = Field(
        default_factory=lambda: get_from_env("AWS_REGION") or "us-east-1")

    # Model Configuration
    model_id: str = "amazon.titan-embed-text-v1"
    normalize: bool = True
    dimensions: Optional[int] = None  # For titan-embed-text-v2

    # Client
    client: Any = None

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Get embeddings from AWS Bedrock.

        Args:
            texts (List[str]): A list of texts to be embedded.
            **kwargs: Additional arguments for model-specific parameters.

        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.

        Raises:
            ValueError: If required configuration is missing or model is not supported.
            Exception: If the API call fails.
        """
        self._initialize_client()

        if self.embedding_model_name is None:
            raise ValueError("Must provide `embedding_model_name` (model_id)")

        # Use embedding_model_name as model_id if provided
        model_id = self.embedding_model_name or self.model_id

        embeddings = []
        for text in texts:
            try:
                # Prepare request body based on model type
                if "titan" in model_id.lower():
                    body = {"inputText": text}
                    if self.normalize:
                        body["normalize"] = True
                    # Only add dimensions for titan-embed-text-v2
                    if "v2" in model_id and self.dimensions is not None:
                        body["dimensions"] = self.dimensions

                elif "cohere" in model_id.lower():
                    body = {
                        "texts": [text],
                        "input_type": kwargs.get("input_type", "search_document")
                    }
                else:
                    raise ValueError(f"Unsupported model: {model_id}")

                # Invoke the model
                response = self.client.invoke_model(
                    modelId=model_id,
                    body=json.dumps(body),
                    contentType="application/json",
                    accept="application/json"
                )

                # Parse response
                response_body = json.loads(response['body'].read())

                # Extract embedding based on model type
                if "titan" in model_id.lower():
                    embedding = response_body.get('embedding')
                elif "cohere" in model_id.lower():
                    embedding = response_body.get('embeddings', [None])[0]
                else:
                    embedding = None

                if embedding is None:
                    raise ValueError(f"Failed to extract embedding from response for model {model_id}")

                embeddings.append(embedding)

            except Exception as e:
                raise Exception(f"Failed to get embedding for text: {str(e)}")

        return embeddings

    async def async_get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Asynchronously get embeddings from AWS Bedrock.

        Note: Currently delegates to synchronous implementation.
        Future versions may use aioboto3 for true async support.

        Args:
            texts (List[str]): A list of texts to be embedded.
            **kwargs: Additional arguments for model-specific parameters.

        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.

        Raises:
            ValueError: If required configuration is missing or model is not supported.
            Exception: If the API call fails.
        """
        # For now, delegate to sync implementation
        # Future: Use aioboto3 for true async support
        return self.get_embeddings(texts, **kwargs)

    def as_langchain(self) -> Any:
        """Convert to LangChain-compatible BedrockEmbeddings instance.

        Returns:
            BedrockEmbeddings: A LangChain BedrockEmbeddings instance.
        """
        self._initialize_client()

        from langchain_community.embeddings import BedrockEmbeddings

        # Use embedding_model_name as model_id if provided
        model_id = self.embedding_model_name or self.model_id

        return BedrockEmbeddings(
            client=self.client,
            model_id=model_id,
            region_name=self.aws_region
        )

    def _initialize_by_component_configer(self,
                                          embedding_configer: ComponentConfiger) -> 'Embedding':
        """Initialize the embedding by the ComponentConfiger object.

        Args:
            embedding_configer(ComponentConfiger): A configer contains embedding configuration.

        Returns:
            Embedding: An AWSBedrockEmbedding instance.
        """
        super()._initialize_by_component_configer(embedding_configer)

        # Load AWS-specific configuration
        if hasattr(embedding_configer, "aws_access_key_id"):
            self.aws_access_key_id = embedding_configer.aws_access_key_id
        if hasattr(embedding_configer, "aws_secret_access_key"):
            self.aws_secret_access_key = embedding_configer.aws_secret_access_key
        if hasattr(embedding_configer, "aws_region"):
            self.aws_region = embedding_configer.aws_region

        # Load model configuration
        if hasattr(embedding_configer, "model_id"):
            self.model_id = embedding_configer.model_id
        if hasattr(embedding_configer, "normalize"):
            self.normalize = embedding_configer.normalize
        if hasattr(embedding_configer, "dimensions"):
            self.dimensions = embedding_configer.dimensions

        return self

    def _initialize_client(self) -> None:
        """Initialize the AWS Bedrock Runtime client.

        Raises:
            ValueError: If required AWS credentials are missing.
        """
        if self.client is not None:
            return

        # Validate required configuration
        if not self.aws_region:
            raise ValueError("AWS_REGION is missing. Please set the AWS_REGION environment variable.")

        try:
            import boto3
            from botocore.config import Config
        except ImportError:
            raise ImportError(
                "boto3 is required for AWS Bedrock embeddings. "
                "Install it with: pip install boto3"
            )

        # Create boto3 session with credentials if provided
        # If not provided, boto3 will use default credential chain (env vars, IAM roles, etc.)
        session_kwargs = {}
        if self.aws_access_key_id:
            session_kwargs['aws_access_key_id'] = self.aws_access_key_id
        if self.aws_secret_access_key:
            session_kwargs['aws_secret_access_key'] = self.aws_secret_access_key
        if self.aws_region:
            session_kwargs['region_name'] = self.aws_region

        session = boto3.Session(**session_kwargs)

        # Create Bedrock Runtime client with retry configuration
        self.client = session.client(
            service_name='bedrock-runtime',
            config=Config(
                retries={
                    'max_attempts': 3,
                    'mode': 'adaptive'
                }
            )
        )
