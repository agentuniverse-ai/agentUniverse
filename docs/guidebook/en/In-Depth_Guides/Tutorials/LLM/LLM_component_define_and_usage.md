# How to definite LLMs
Based on the design characteristics of the domain components of agentUniverse, creating a model LLM definition consists of two parts:

* llm_xx.yaml
* llm_xx.py 

The `llm_xx.yaml` must be created; it includes important property information such as the LLM component's name, description, and model name. The `llm_xx.py` is created as needed and contains the specific behavior of the LLM component, supporting user-standard behavior customization injection for the LLM. Understanding this principle, let's look at how to create these two parts in detail.

## Creating LLM Configuration llm_xx.yaml
We will detail the various components within the configuration.

### Setting the basic attributes of the LLM.
* `name`: The name of the LLM, the name of the LLM instance. You can set any name as per your preference.
* `description`: Description of the LLM, fill in according to your actual needs.
* `model_name`: The official name of the accessed LLM model, such as `gpt-4o`, `gpt-3.5-turbo` etc., from the OpenAI series.
* `streaming`: Whether the LLM is streaming (optional, default is False)  
* `max_retries`: The maximum number of retries for LLM access (optional)  
* `max_tokens`: The maximum number of tokens for the LLM model instance output (optional)  
* `api_key`: The API key for the LLM model instance (optional)  
* `api_base`: The endpoint for the LLM model instance request (optional)  
* `organization`: The organization for the LLM model instance (optional)  
* `proxy`: The proxy address for the LLM model instance request (optional)

### Setting LLM Component Metadata
**`metadata` - metadata of component**
* `type`: The component type, 'LLM'
* `module`: Path to the LLM entity package
* `class`: Name of the LLM entity class

All the provided LLM components will include the corresponding `module` and `class` information, which can be copied directly into this section. This part integrates all the configuration of the LLM component with its behavior to form a complete unit. If you have defined standard behavior for the LLM, then you will need to fill in this section according to the actual path. We will provide further explanation in the subsequent section on [Creating from Existing LLMs Object](#Creating from Existing LLMs Object).

### An actual example of an LLM configuration definition.
```yaml
name: 'demo_customized_llm'
description: 'demo customized llm'
model_name: 'gpt-4o'
max_tokens: 1000
max_retries: 2
temperature: 0.5
streaming: True
api_key: '${OPENAI_API_KEY}'
api_base: 'https://api.openai.com/v1'
organization: '${OPENAI_ORGANIZATION}'
proxy: '${OPENAI_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.default_openai_llm'
  class: 'DefaultOpenAILLM'
```

The above is an actual example of an LLM configuration. 

**Note:**

The model parameters such as `api_key`, `api_base`, `organization`, and `proxy` can be configured in three ways:

1. Direct String Value: Enter the API key string directly in the configuration file.

    ```yaml
    api_key: 'sk-xxx'
    ```

2. Environment Variable Placeholder: Use the `${VARIABLE_NAME}` syntax to load from environment variables. When `agentUniverse` is launched, it will automatically read the corresponding value from the environment variables.

    ```yaml
    api_key: '${OPENAI_API_KEY}'
    ```

3. Custom Function Loading: Use the `@FUNC` annotation to dynamically load the API key via a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="openai"))'
    ```

    The function needs to be defined in the `YamlFuncExtension` class within the `yaml_func_extension.py` file. You can refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When `agentUniverse` loads this configuration:
   - It parses the `@FUNC` annotation.
   - Executes the `load_api_key` function with the corresponding parameters.
   - Replaces the annotation content with the function's return value.

In addition to the standard configuration items introduced above, you can find more examples of LLM configuration YAMLs in our sample project under the path `sample_standard_app.intelligence.agentic.llm`.

Furthermore, agentuniverse does not restrict users from extending the LLM YAML configuration content. You can create any custom configuration keys according to your requirements, but please be careful not to duplicate the default configuration keywords mentioned above.

## Creating LLM Domain Behavior Definition - llm_xx.py
In this section, you can extend the behavior of any LLM; however, this part is not necessary if you are completely using the existing LLM capabilities.

In this section, we will focus on introducing the common behavior definitions of LLMs and the techniques that you might use in the actual LLM behavior definition process.

### Creating an LLM class object
Create the corresponding LLM class object and inherit from the `LLM` base class of the agentUniverse framework.

### Customizing the Corresponding LLM Domain Behavior
Common customizable LLM behaviors are as follows.

#### _new_client method
We know that many model services have provided standard client SDKs. In this method, you can inject the official client provided by the LLM service. If the model you are using does not offer a standard client, this step is not necessary.

```python
def _new_client(self):
        """Initialize the client."""
        pass
```

#### _new_async_client method
Similar to the `_new_client` method, in this method, you can inject the official asynchronous client provided by the LLM service. If the model you are using does not offer a standard asynchronous client, this step is not necessary.

```python
def _new_async_client(self):
        """Initialize the async client."""
        pass
```

#### The call and acall methods
The LLM base class provides two abstract methods: call (for synchronous calling) and acall (for asynchronous calling). Users can customize the model invocation by implementing the call and acall methods.
Their standard definitions are as follows:
```python
from abc import abstractmethod
from typing import Optional, Any, AsyncIterator, Iterator, Union
from agentuniverse.llm.llm_output import LLMOutput

@abstractmethod
def call(self, *args: Any, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
    """Run the LLM."""

@abstractmethod
async def acall(self, *args: Any, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
    """Asynchronously run the LLM."""
```

#### The as_langchain method
agentUniverse utilizes the capabilities of langchain at a lower level. It is compatible with the LLM definition methods used by langchain. If your project has already been using langchain, then all you need to do in this method is to incorporate the BaseLanguageModel, which is a fundamental model from the Langchain framework, to merge agentUniverse with langchain. agentUniverse can support integration with any similar orchestration framework, such as Semantic Kernel, though currently, our focus is on langchain.

```python
from langchain_core.language_models.base import BaseLanguageModel

def as_langchain(self) -> BaseLanguageModel:
        """Convert to the langchain llm class."""
        pass
```

#### The max_context_length method
This method defines the maximum context length for an LLM model. For example, the max_context_length method returns 8192 for GPT-4 and 4096 for GPT-3.5-turbo. This information can be found in the model's official documentation.

#### The get_num_tokens method
The get_num_tokens method defines the model's encoding method and the way tokens are counted. It takes the input data and outputs the corresponding number of tokens.

#### An Actual Example of LLM Domain Behavior Definition
Taking the OpenAI LLM series as an example, let's consider OpenAILLM.py.

```python
from typing import Any, Optional, AsyncIterator, Iterator, Union

import httpx
from langchain_core.language_models.base import BaseLanguageModel
from openai import OpenAI, AsyncOpenAI
from pydantic import Field
import tiktoken

from agentuniverse.llm.langchain_instance import LangchainOpenAI
from agentuniverse.llm.llm import LLM, LLMOutput
from agentuniverse.base.util.env_util import get_from_env

OPENAI_MAX_CONTEXT_LENGTH = {
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-0301": 4096,
    "gpt-3.5-turbo-0613": 4096,
    "gpt-3.5-turbo-16k": 16384,
    "gpt-3.5-turbo-16k-0613": 16384,
    "gpt-35-turbo": 4096,
    "gpt-35-turbo-16k": 16384,
    "gpt-3.5-turbo-1106": 16384,
    "gpt-3.5-turbo-0125": 16384,
    "gpt-4-0314": 8192,
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-32k-0613": 32768,
    "gpt-4-0613": 8192,
    "gpt-4-1106-preview": 128000,
    "gpt-4-turbo": 128000,
    "gpt-4o": 128000,
    "gpt-4o-2024-05-13": 128000,
}


class OpenAILLM(LLM):
    """The openai llm class.

    Attributes:
        openai_api_key (Optional[str], optional): The API key for the OpenAI API.
        This automatically infers the `openai_api_key` from the environment variable `OPENAI_API_KEY` if not provided.

        openai_organization (Optional[str], optional): The OpenAI organization.
        This automatically infers the `openai_organization` from the environment variable `OPENAI_ORGANIZATION` if not provided.

        openai_api_base (Optional[str], optional): The OpenAI base url.
        This automatically infers the `openai_api_base` from the environment variable `OPENAI_API_BASE` if not provided.

        openai_client_args (Optional[dict], optional): Additional arguments to pass to the OpenAI client.
   """

    openai_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_API_KEY"))
    openai_organization: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_ORGANIZATION"))
    openai_api_base: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_API_BASE"))
    openai_proxy: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_PROXY"))
    openai_client_args: Optional[dict] = None

    def _new_client(self):
        """Initialize the openai client."""
        return OpenAI(
            api_key=self.openai_api_key,
            organization=self.openai_organization,
            base_url=self.openai_api_base,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
            http_client=httpx.Client(proxy=self.openai_proxy) if self.openai_proxy else None,
            **(self.openai_client_args or {}),
        )

    def _new_async_client(self):
        """Initialize the openai async client."""
        return AsyncOpenAI(
            api_key=self.openai_api_key,
            organization=self.openai_organization,
            base_url=self.openai_api_base,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
            http_client=httpx.AsyncClient(proxy=self.openai_proxy) if self.openai_proxy else None,
            **(self.openai_client_args or {}),
        )

    def call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Run the OpenAI LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.streaming
        self.client = self._new_client()
        with self.client as client:
            chat_completion = client.chat.completions.create(
                messages=messages,
                model=kwargs.pop('model', self.model_name),
                temperature=kwargs.pop('temperature', self.temperature),
                stream=kwargs.pop('stream', streaming),
                max_tokens=kwargs.pop('max_tokens', self.max_tokens),
                **kwargs,
            )
            if not streaming:
                text = chat_completion.choices[0].message.content
                return LLMOutput(text=text, raw=chat_completion.model_dump())
            return self.generate_stream_result(chat_completion)

    async def acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronously run the OpenAI LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.streaming
        self.async_client = self._new_async_client()
        async with self.async_client as async_client:
            chat_completion = await async_client.chat.completions.create(
                messages=messages,
                model=kwargs.pop('model', self.model_name),
                temperature=kwargs.pop('temperature', self.temperature),
                stream=kwargs.pop('stream', streaming),
                max_tokens=kwargs.pop('max_tokens', self.max_tokens),
                **kwargs,
            )
            if not streaming:
                text = chat_completion.choices[0].message.content
                return LLMOutput(text=text, raw=chat_completion.model_dump())
            return self.agenerate_stream_result(chat_completion)

    def as_langchain(self) -> BaseLanguageModel:
        """Convert the AgentUniverse(AU) openai llm class to the langchain openai llm class."""
        return LangchainOpenAI(self)

    def max_context_length(self) -> int:
        """Max context length.

          The total length of input tokens and generated tokens is limited by the openai model's context length.
          """
        return OPENAI_MAX_CONTEXT_LENGTH.get(self.model_name, 4096)

    def get_num_tokens(self, text: str) -> int:
        """Get the number of tokens present in the text.

        Useful for checking if an input will fit in an openai model's context window.

        Args:
            text: The string input to tokenize.

        Returns:
            The integer number of tokens in the text.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    @staticmethod
    def parse_result(chunk):
        """Generate the result of the stream."""
        chat_completion = chunk
        if not isinstance(chunk, dict):
            chunk = chunk.dict()
        if len(chunk["choices"]) == 0:
            return
        choice = chunk["choices"][0]
        message = choice.get("delta")
        text = message.get("content")
        if not text:
            return
        return LLMOutput(text=text, raw=chat_completion.model_dump())

    @classmethod
    def generate_stream_result(cls, stream: Iterator) -> Iterator[LLMOutput]:
        """Generate the result of the stream."""
        for chunk in stream:
            llm_output = cls.parse_result(chunk)
            if llm_output:
                yield llm_output

    @classmethod
    async def agenerate_stream_result(cls, stream: AsyncIterator) -> AsyncIterator[LLMOutput]:
        """Generate the result of the stream."""
        async for chunk in stream:
            llm_output = cls.parse_result(chunk)
            if llm_output:
                yield llm_output
```
In the aforementioned example, we connect to the standard OpenAI client SDK through the `_new_client` and `_new_async_client` methods. The implementation of `call` and `acall` accomplishes the standard synchronous and asynchronous invocation methods of OpenAI. By introducing the LangchainOpenAI object in `as_langchain`, we complete the integration with the langchain framework.

LangchainOpenAI.py is an object of the BaseLanguageModel from langchain. You can refer to the following example.

```python
from typing import Any, List, Optional, AsyncIterator

from langchain.callbacks.manager import AsyncCallbackManagerForLLMRun, CallbackManagerForLLMRun
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage, ChatResult
from langchain_community.chat_models.openai import _convert_delta_to_message_chunk
from langchain_core.language_models.chat_models import generate_from_stream, agenerate_from_stream
from langchain_core.messages import AIMessageChunk
from langchain_core.outputs import ChatGenerationChunk

from agentuniverse.llm.llm import LLM


class LangchainOpenAI(ChatOpenAI):
    """Langchain OpenAI LLM wrapper."""

    llm: Optional[LLM] = None

    def __init__(self, llm: LLM):
        """The __init__ method.

        The agentUniverse LLM instance is passed to this class as an argument.
        Convert the attributes of AgentUniverse(AU) LLM instance to the LangchainOpenAI object for initialization

        Args:
            llm (LLM): the AgentUniverse(AU) LLM instance.
        """
        init_params = dict()
        init_params['model_name'] = llm.model_name if llm.model_name else 'gpt-3.5-turbo'
        init_params['temperature'] = llm.temperature if llm.temperature else 0.7
        init_params['request_timeout'] = llm.request_timeout
        init_params['max_tokens'] = llm.max_tokens
        init_params['max_retries'] = llm.max_retries if llm.max_retries else 2
        init_params['streaming'] = llm.streaming if llm.streaming else False
        init_params['openai_api_key'] = llm.openai_api_key if llm.openai_api_key else 'blank'
        init_params['openai_organization'] = llm.openai_organization
        init_params['openai_api_base'] = llm.openai_api_base
        init_params['openai_proxy'] = llm.openai_proxy
        super().__init__(**init_params)
        self.llm = llm

    def _generate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            stream: Optional[bool] = None,
            **kwargs,
    ) -> ChatResult:
        """Run the Langchain OpenAI LLM."""
        should_stream = stream if stream is not None else self.streaming
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs}
        llm_output = self.llm.call(messages=message_dicts, **params)
        if not should_stream:
            return self._create_chat_result(llm_output.raw)
        stream_iter = self.as_langchain_chunk(llm_output)
        return generate_from_stream(stream_iter)

    async def _agenerate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
            stream: Optional[bool] = None,
            **kwargs: Any,
    ) -> ChatResult:
        """Asynchronously run the Langchain OpenAI LLM."""
        should_stream = stream if stream is not None else self.streaming
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs}
        llm_output = await self.llm.acall(messages=message_dicts, **params)
        if not should_stream:
            return self._create_chat_result(llm_output.raw)
        stream_iter = self.as_langchain_achunk(llm_output)
        return await agenerate_from_stream(stream_iter)

    @staticmethod
    def as_langchain_chunk(stream, run_manager=None):
        default_chunk_class = AIMessageChunk
        for llm_result in stream:
            chunk = llm_result.raw
            if not isinstance(chunk, dict):
                chunk = chunk.dict()
            if len(chunk["choices"]) == 0:
                continue
            choice = chunk["choices"][0]
            chunk = _convert_delta_to_message_chunk(
                choice["delta"], default_chunk_class
            )
            finish_reason = choice.get("finish_reason")
            generation_info = (
                dict(finish_reason=finish_reason) if finish_reason is not None else None
            )
            default_chunk_class = chunk.__class__
            chunk = ChatGenerationChunk(message=chunk, generation_info=generation_info)
            yield chunk
            if run_manager:
                run_manager.on_llm_new_token(chunk.text, chunk=chunk)

    @staticmethod
    async def as_langchain_achunk(stream_iterator: AsyncIterator, run_manager=None) \
            -> AsyncIterator[ChatGenerationChunk]:
        default_chunk_class = AIMessageChunk
        async for llm_result in stream_iterator:
            chunk = llm_result.raw
            if not isinstance(chunk, dict):
                chunk = chunk.dict()
            if len(chunk["choices"]) == 0:
                continue
            choice = chunk["choices"][0]
            chunk = _convert_delta_to_message_chunk(
                choice["delta"], default_chunk_class
            )
            finish_reason = choice.get("finish_reason")
            generation_info = (
                dict(finish_reason=finish_reason) if finish_reason is not None else None
            )
            default_chunk_class = chunk.__class__
            chunk = ChatGenerationChunk(message=chunk, generation_info=generation_info)
            yield chunk
            if run_manager:
                await run_manager.on_llm_new_token(token=chunk.text, chunk=chunk)
```

Within the integration object of agentUniverse and langchain, you only need to refactor the `_generate` and `_agenerate` methods of the langchain's LLM model. The focus here is on utilizing the `self.llm.call` and `self.llm.acall` methods. Other aspects will be mentioned in the practical tips section later on and will not be elaborated here.

## Pay attention to the package path where your defined LLM is located.

With the above configuration and domain definition of LLM, you have mastered all the steps of creating an LLM definition. Next, we will use these LLMs, but before using them, please ensure that the created LLM is within the correct package scan path.

In the config.toml of the agentUniverse project, you need to configure the package corresponding to the LLM file. Please confirm again whether the package path where your created file is located is under the `CORE_PACKAGE` 's `llm` path or its subpath.

Here is an example configuration from the sample project, as follows:

```yaml
[CORE_PACKAGE]
# Scan and register llm components for all paths under this list, with priority over the default.
llm = ['sample_standard_app.intelligence.agentic.llm']
```

## Pay attention to the API key associated with the LLM you are using.

The basic parameters of the API key for the model, such as openai_api_key, openai_organization, openai_base, openai_proxy, etc., can be configured as system environment variables. The model object will read the corresponding system environment variables during the initialization process to assemble the parameters. In addition, you can also configure secret keys and other information in the custom_key.toml of agentUniverse (we recommend that you place such configurations outside the project or exclude them from tracking in .gitignore to avoid key information being tracked by git and leaked). During the initialization process of the agentUniverse system, it will automatically read the configuration file and register the configuration information to the system environment variables.

Below is an actual configuration of `custom_key.toml`:
```toml
# Example file of custom_key.toml. Rename to custom_key.toml while using.
[KEY_LIST]
# Perform a full component scan and registration for all the paths under this list.
SERPER_API_KEY='xxx'
OPENAI_API_KEY='xxx'
OPENAI_API_BASE ='xxx'
OPENAI_ORGANIZATION = 'xxx'
OPENAI_PROXY = 'xxx'
```

## Other Tips for Creating LLM Model Components
### Adding LLM Streaming Capabilities
In the example provided in [Customizing the Corresponding LLM Domain Behavior](#An Actual Example of LLM Domain Behavior Definition), streaming capabilities have already been outlined. You can focus on the methods `generate_stream_result` and `agenerate_stream_result` within `call` and `acall`.

If you are using the Langchain-related LLM class and need to implement streaming return in `_generate` and `_agenerate`, you should pay particular attention to the methods `as_langchain_chunk` and `as_langchain_achunk` in the example LangchainOpenAI.py.

### Creating from Existing LLMs Object
agentUniverse allows for the quick creation of LLM instances from existing LLM component objects.

For example, the OpenAI LLM series is provided by the framework, and its standard metadata is as follows:
```text
module: 'agentuniverse.llm.default.default_openai_llm'
class: 'DefaultOpenAILLM'
```

If we need to configure and define an LLM instance based on the `gpt-4o`, with a maximum token limit of 1000 and a retry count is 2, the configuration would be as follows:
```yaml
name: 'demo_llm'
description: 'demo openai'
model_name: 'gpt-4o'
max_tokens: 1000
max_retries: 2
streaming: True
api_key: '${OPENAI_API_KEY}'
api_base: 'https://api.openai.com/v1'
organization: '${OPENAI_ORGANIZATION}'
proxy: '${OPENAI_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.default_openai_llm'
  class: 'DefaultOpenAILLM'
```

You can find more LLM metadata in the [Understanding More Existing LLM Components](#Understanding More Existing LLM Components) section of this document.

# How to Use Model LLM Components
## Configure for use in an Agent
You can set up any LLM you have created in the llm_model of your agent according to the contents of [Agent Creation and Usage section](../Agent/Agent_Create_And_Use.md).

Refer to the example: `demo_agent`, with the specific file path being `agentUniverse/examples/sample_standard_app/intelligence/agentic/agent/agent_instance/demo_agent.yaml`.

## Using the LLM Manager
You can obtain an LLM instance with the specified name through the `.get_instance_obj(xx_llm_name)` method in the LLM Manager.

```python
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager

llm: LLM = LLMManager().get_instance_obj('llm_name')
```

# Understanding More Existing LLM Components
The framework provides additional LLM components under the package path `agentuniverse.llm.default`. You can further inspect the corresponding code or learn more about them in our extended component introduction section.


# Conclusion
By now, you have mastered the definition and use of model LLMs. Go ahead and try defining and using LLMs.