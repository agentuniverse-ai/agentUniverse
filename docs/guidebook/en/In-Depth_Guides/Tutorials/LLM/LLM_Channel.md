## Model Channel Definition

In agentUniverse, model channels are implemented to manage different channels for the same type of model. Through proper configuration of the model channel component, you can easily switch between different channels to smoothly call model services provided by different service providers.

## Model Channel Call Flow

![llm_channel](../../../../_picture/llm_channel.jpg)

When agentUniverse starts up, during the LLM model component initialization phase, it reads the channel name configured in the llm yaml and connects the configured model channel to the corresponding model component.

When a model is called, if there is an associated channel, it calls the corresponding model channel's call method, completes the channel connection, and returns the model channel execution result.

### Specific Code

Code location: agentuniverse.llm.llm.LLM

```python
    def init_channel(self):
    """
    Initialize the model channel method. When users configure the channel parameter in yaml, initialize the model channel and pass model parameters to the specified channel.
    """
    if self.channel and not self._channel_instance:
        llm_channel: LLMChannel = LLMChannelManager().get_instance_obj(
            component_instance_name=self.channel)
        if not llm_channel:
            return

        self._channel_instance = llm_channel

        llm_attrs = vars(self)
        channel_model_config = {}

        for attr_name, attr_value in llm_attrs.items():
            channel_model_config[attr_name] = attr_value

        llm_channel.channel_model_config = channel_model_config


def call(self, *args: Any, **kwargs: Any):
    try:
        self.init_channel()
        # If channel instance exists, execute channel call method
        if self._channel_instance:
            return self._channel_instance.call(*args, **kwargs)
        return self._call(*args, **kwargs)
    except Exception as e:
        LOGGER.error(f'Error in LLM call: {e}')
        raise e


async def acall(self, *args: Any, **kwargs: Any):
    try:
        self.init_channel()
        # If channel instance exists, execute channel acall method
        if self._channel_instance:
            return await self._channel_instance.acall(*args, **kwargs)
        return await self._acall(*args, **kwargs)
    except Exception as e:
        LOGGER.error(f'Error in LLM acall: {e}')
        raise e


def as_langchain(self) -> BaseLanguageModel:
    """Convert to the langchain llm class."""
    self.init_channel()
    # If channel instance exists, execute channel's langchain model conversion method
    if self._channel_instance:
        return self._channel_instance.as_langchain()
    pass
```

## Model Channel Configurable Parameters

In agentUniverse, the Model Channel (LLMChannel) class inherits from ComponentBase and includes the following configurable parameters:

1. `channel_name`: (Required) Corresponds to the aU channel component instance name
2. `channel_api_key`: (Required) Corresponds to the specific channel's key, e.g., DASHSCOPE_API_KEY for Aliyun Dashscope platform; QIANFAN_API_KEY for Baidu Qianfan platform
3. `channel_api_base`: (Required) Corresponds to the specific channel's endpoint
4. `channel_organization`: (Optional) Corresponds to the specific channel's organization
5. `channel_proxy`: (Optional) Corresponds to the specific channel's proxy
6. `channel_model_name`: (Required) Corresponds to the specific channel's model name. For example: deepseek-r1's model_name is deepseek-reasoner on the official website, but deepseek-r1 on the Baichuan platform
7. `channel_ext_info`: (Optional) Corresponds to the specific channel's extended information
8. `model_support_stream`: (Optional) Determines whether the current channel's model supports streaming. For example, if deepseek-r1 doesn't support streaming calls in a certain channel, this parameter should be set to False to force the streaming switch to be off during channel calls
9. `model_support_max_context_length`: (Optional) Determines the maximum context length supported by the current channel's model. For example, if deepseek-r1's maximum context length in a certain channel differs from the official model's context length, this parameter serves as a calibration function
10. `model_is_openai_protocol_compatible`: (Optional) Determines whether the current channel's model supports the OpenAI protocol, default is True
11. `_channel_model_config`: Inherits the model parameters configured in llm yaml. When llm initializes the channel, these parameters are assigned to the channel

## Specific Configuration Examples

### Official Channel

Each model in aU has an official model channel, such as deepseek-r1-official, qwen-max-official.

Here we use deepseek-r1 as an example to show its official channel configuration:

#### deepseek r1 llm yaml configuration

```yaml
name: 'deepseek-reasoner'
description: 'deepseek-reasoner'
model_name: 'deepseek-reasoner'
temperature: 0.5
max_tokens: 2000
max_context_length: 65792
streaming: True
channel: deepseek-r1-official # Configure model channel as official channel
meta_class: 'agentuniverse.llm.default.deep_seek_openai_style_llm.DefaultDeepSeekLLM'
```

#### deepseek r1 official channel yaml configuration

```yaml
channel_name: 'deepseek-r1-official'
channel_api_key: '${DEEPSEEK_API_KEY}' # deepseek-r1 official website key
channel_api_base: 'https://api.deepseek.com/v1' # deepseek-r1 official website url
channel_model_name: 'deepseek-reasoner' # deepseek-r1 official website model name
model_support_stream: True # Whether deepseek-r1 official channel supports streaming
model_support_max_context_length: 65792 # Maximum context length supported by deepseek-r1 official channel model
model_is_openai_protocol_compatible: True
meta_class: 'agentuniverse.llm.llm_channel.deepseek_official_llm_channel.DeepseekOfficialLLMChannel'
```

### Alibaba Cloud Baichuan Channel

Using deepseek-r1 as an example, here's the specific configuration for the Baichuan channel.

#### deepseek-r1 model yaml configuration:

```yaml
name: 'deepseek-reasoner'
description: 'deepseek-reasoner'
model_name: 'deepseek-reasoner'
temperature: 0.5
max_tokens: 2000
max_context_length: 65792
streaming: True
channel: deepseek-r1-dashscope # Configure model channel as dashscope channel
meta_class: 'agentuniverse.llm.default.deep_seek_openai_style_llm.DefaultDeepSeekLLM'
```

#### Baichuan dashscope channel configuration:

```yaml
channel_name: 'deepseek-r1-dashscope'
channel_api_key: '${DASHSCOPE_API_KEY}' # Alibaba Cloud Baichuan platform key
channel_api_base: 'https://dashscope.aliyuncs.com/compatible-mode/v1' # Alibaba Cloud Baichuan platform url
channel_model_name: deepseek-r1 # Alibaba Cloud Baichuan platform model name
model_support_stream: True # Whether Alibaba Cloud Baichuan platform model supports streaming
model_support_max_context_length: 65792 # Maximum context length supported by Alibaba Cloud Baichuan platform model
model_is_openai_protocol_compatible: True
meta_class: 'agentuniverse.llm.llm_channel.dashscope_llm_channel.DashscopeLLMChannel'
```

### Ollama Channel

Using deepseek-r1 as an example, here's the specific configuration for the Ollama channel.

#### deepseek-r1 model yaml configuration:

```yaml
name: 'deepseek-reasoner'
description: 'deepseek-reasoner'
model_name: 'deepseek-reasoner'
temperature: 0.5
max_tokens: 2000
max_context_length: 65792
streaming: True
channel: deepseek-r1-ollama # Configure model channel as ollama channel
meta_class: 'agentuniverse.llm.default.deep_seek_openai_style_llm.DefaultDeepSeekLLM'
```

#### Ollama channel configuration:

```yaml
channel_name: 'deepseek-r1-ollama'
channel_api_base: 'http://localhost:11434'
channel_model_name: deepseek-r1:671b, # deepseek-r1 model name in ollama channel
support_stream: True # Whether deepseek-r1 supports streaming in ollama channel
support_max_context_length: 65536 # Maximum context length supported by deepseek-r1 in ollama channel
is_openai_protocol_compatible: False # Whether deepseek-r1 is compatible with OpenAI protocol in ollama channel
meta_class: 'agentuniverse.llm.llm_channel.ollama_llm_channel.OllamaLLMChannel'
```

## Currently Built-in Model Channels in agentUniverse:

### official_llm_channel

Each built-in model in agentUniverse has an official channel, such as:

[kimi_official_llm_channel](../../../../../../agentuniverse/llm/llm_channel/kimi_official_llm_channel.py)
[openai_official_llm_channel](../../../../../../agentuniverse/llm/llm_channel/openai_official_llm_channel.py)
[deepseek_official_llm_channel](../../../../../../agentuniverse/llm/llm_channel/deepseek_official_llm_channel.py)

### dashscope_llm_channel

Alibaba Cloud Baichuan platform model channel: [dashscope_llm_channel](../../../../../../agentuniverse/llm/llm_channel/dashscope_llm_channel.py)

Note: The official channel for qwen model is dashscope_llm_channel

### qianfan_llm_channel

Baidu Cloud Qianfan platform model channel: [qianfan_llm_channel](../../../../../../agentuniverse/llm/llm_channel/qianfan_llm_channel.py)

### ollama_llm_channel

Ollama platform model channel: [ollama_llm_channel](../../../../../../agentuniverse/llm/llm_channel/ollama_llm_channel.py)

## Usage Recommendations

1. When configuring model channels, ensure all necessary parameters are correctly set, especially critical parameters like channel_api_key and channel_api_base.
2. For different channels, model_support_stream and model_support_max_context_length may vary, so it's recommended to configure them according to actual circumstances. 