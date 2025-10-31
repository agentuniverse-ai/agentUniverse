#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time : 2025/10/28 19:30
# @Author : veteran
# @FileName : aws_bedrock_llm.py

from typing import Optional, Any, Union, Iterator, AsyncIterator
import json

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm import LLM, LLMOutput

# Define maximum context lengths for different AWS Bedrock models
AWS_BEDROCK_MAX_CONTEXT_LENGTH = {
    "amazon.nova-pro-v1:0": 300000,
    "amazon.nova-lite-v1:0": 300000,
    "amazon.nova-micro-v1:0": 128000,
    "anthropic.claude-3-5-sonnet-20240620-v1:0": 200000,
    "anthropic.claude-3-sonnet-20240229-v1:0": 200000,
    "anthropic.claude-3-haiku-20240307-v1:0": 200000,
    "anthropic.claude-3-opus-20240229-v1:0": 200000,
    "anthropic.claude-v2:1": 200000,
    "anthropic.claude-v2": 100000,
    "anthropic.claude-instant-v1": 100000,
    "meta.llama3-70b-instruct-v1:0": 8192,
    "meta.llama3-8b-instruct-v1:0": 8192,
    "mistral.mistral-7b-instruct-v0:2": 32000,
    "mistral.mixtral-8x7b-instruct-v0:1": 32000,
    "mistral.mistral-large-2402-v1:0": 32000,
    "cohere.command-r-plus-v1:0": 128000,
    "cohere.command-r-v1:0": 128000,
    "amazon.titan-text-premier-v1:0": 32000,
    "amazon.titan-text-express-v1": 8000,
    "amazon.titan-text-lite-v1": 4000,
}


class AWSBedrockLLM(LLM):
    """
        AWS Bedrock LLM using boto3 client
        
        This class provides integration with AWS Bedrock models using the native boto3 API.
        AWS Bedrock supports various foundation models including Claude, Llama, Mistral, Nova, and more.
        
        Args:
            aws_access_key_id: AWS access key ID (optional, can use AWS credentials chain)
            aws_secret_access_key: AWS secret access key (optional, can use AWS credentials chain)
            aws_session_token: AWS session token for temporary credentials (optional)
            aws_region: AWS region where Bedrock is available (e.g., us-east-1, us-west-2)
    """

    aws_access_key_id: Optional[str] = Field(default_factory=lambda: get_from_env("AWS_ACCESS_KEY_ID"))
    aws_secret_access_key: Optional[str] = Field(default_factory=lambda: get_from_env("AWS_SECRET_ACCESS_KEY"))
    aws_session_token: Optional[str] = Field(default_factory=lambda: get_from_env("AWS_SESSION_TOKEN"))
    aws_region: Optional[str] = Field(default_factory=lambda: get_from_env("AWS_REGION") or "us-east-1")

    def __init__(self, **data):
        """Initialize AWS Bedrock LLM."""
        super().__init__(**data)
        self._client = None

    def _get_client(self):
        """Get or create boto3 bedrock-runtime client."""
        if self._client is None:
            try:
                import boto3
            except ImportError:
                raise ImportError("boto3 is required for AWS Bedrock LLM. Install it with: pip install boto3")
            
            session_kwargs = {
                'region_name': self.aws_region,
            }
            if self.aws_access_key_id:
                session_kwargs['aws_access_key_id'] = self.aws_access_key_id
            if self.aws_secret_access_key:
                session_kwargs['aws_secret_access_key'] = self.aws_secret_access_key
            if self.aws_session_token:
                session_kwargs['aws_session_token'] = self.aws_session_token
            
            self._client = boto3.client('bedrock-runtime', **session_kwargs)
        return self._client

    def _convert_messages_format(self, messages: list) -> list:
        """Convert messages from OpenAI format to Bedrock format."""
        bedrock_messages = []
        for msg in messages:
            role = msg.get('role')
            content = msg.get('content')
            
            # Bedrock uses 'user' and 'assistant' roles
            if role == 'system':
                # System messages need to be converted to user messages in Bedrock
                role = 'user'
            
            # Convert content to Bedrock format
            if isinstance(content, str):
                bedrock_content = [{"text": content}]
            else:
                bedrock_content = content
            
            bedrock_messages.append({
                "role": role,
                "content": bedrock_content
            })
        
        return bedrock_messages

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Call the AWS Bedrock LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        streaming = kwargs.pop("streaming", self.streaming)
        client = self._get_client()
        
        # Convert messages to Bedrock format
        bedrock_messages = self._convert_messages_format(messages)
        
        # Prepare inference config
        inference_config = {
            "maxTokens": kwargs.pop("max_tokens", self.max_tokens or 512),
            "temperature": kwargs.pop("temperature", self.temperature or 0.7),
        }
        
        if "top_p" in kwargs:
            inference_config["topP"] = kwargs.pop("top_p")
        
        try:
            if streaming:
                # Streaming response
                response = client.converse_stream(
                    modelId=self.model_name,
                    messages=bedrock_messages,
                    inferenceConfig=inference_config,
                )
                return self._generate_stream_result(response)
            else:
                # Non-streaming response
                response = client.converse(
                    modelId=self.model_name,
                    messages=bedrock_messages,
                    inferenceConfig=inference_config,
                )
                
                # Extract response text
                output_message = response['output']['message']
                text = output_message['content'][0]['text']
                
                return LLMOutput(text=text, raw=response)
        
        except Exception as e:
            raise RuntimeError(f"Error calling AWS Bedrock: {e}")

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Async call to AWS Bedrock LLM.
        
        Note: boto3 doesn't support async natively, so this is a sync call wrapped.
        For true async, consider using aioboto3.
        """
        streaming = kwargs.get("streaming", self.streaming)
        result = self._call(messages, **kwargs)
        
        # If streaming, wrap the generator in an async generator
        if streaming:
            return self._async_generator_wrapper(result)
        return result
    
    async def _async_generator_wrapper(self, sync_generator):
        """Wrap a sync generator to make it async."""
        for item in sync_generator:
            yield item

    def _generate_stream_result(self, stream) -> Iterator[LLMOutput]:
        """Generate streaming results from Bedrock response."""
        try:
            for event in stream['stream']:
                if 'contentBlockDelta' in event:
                    delta = event['contentBlockDelta']['delta']
                    if 'text' in delta:
                        yield LLMOutput(text=delta['text'], raw=event)
                elif 'messageStop' in event:
                    # End of message
                    break
        except Exception as e:
            raise RuntimeError(f"Error in streaming response: {e}")

    def max_context_length(self) -> int:
        """Return the maximum context length for the model."""
        if self._max_context_length:
            return self._max_context_length
        return AWS_BEDROCK_MAX_CONTEXT_LENGTH.get(self.model_name, 8000)

    def get_num_tokens(self, text: str) -> int:
        """Get the number of tokens in the text.
        
        Note: This is an approximation. For accurate token counting,
        you would need to use the specific tokenizer for each model.
        """
        # Simple approximation: ~4 characters per token
        return len(text) // 4

    def as_langchain(self):
        """Convert to LangChain LLM.
        
        Note: This requires langchain-aws package.
        """
        try:
            from langchain_aws import ChatBedrock
            
            return ChatBedrock(
                model_id=self.model_name,
                region_name=self.aws_region,
                credentials_profile_name=None,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                aws_session_token=self.aws_session_token,
            )
        except ImportError:
            raise ImportError(
                "langchain-aws is required for LangChain integration. "
                "Install it with: pip install langchain-aws"
            )
