# Mistral AI LLM Usage

## Mistral AI LLM

`MistralLLM` connects to Mistral AI's OpenAI-compatible API endpoint (La Plateforme). Supports Mistral Large (128k context), Nemo, Codestral, and all models on La Plateforme. Environment variables: `MISTRAL_API_KEY`, `MISTRAL_API_BASE` (default `https://api.mistral.ai/v1`). Copy `mistral_llm.yaml.example` to configure.

## 1. Create the relevant file.
Create a YAML file, for example, `user_mistral_llm.yaml`. Paste the following content into your `user_mistral_llm.yaml` file.

```yaml
name: 'user_mistral_llm'
description: 'default mistral llm with spi'
model_name: 'mistral-large-latest'
max_tokens: 4096
temperature: 0.7
api_key: '${MISTRAL_API_KEY}'
api_base: '${MISTRAL_API_BASE}'
proxy: '${MISTRAL_PROXY}'
streaming: False
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.mistral_llm'
  class: 'MistralLLM'
```

**Note:**

The model parameters such as `api_key`, `api_base`, and `proxy` can be configured in three ways:

1. Direct String Value: Enter the API key string directly in the configuration file.

    ```yaml
    api_key: 'xxx'
    ```

2. Environment Variable Placeholder: Use the `${VARIABLE_NAME}` syntax to load from environment variables. When `agentUniverse` is launched, it will automatically read the corresponding value from the environment variables.

    ```yaml
    api_key: '${MISTRAL_API_KEY}'
    ```

3. Custom Function Loading: Use the `@FUNC` annotation to dynamically load the API key via a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="mistral"))'
    ```

    The function needs to be defined in the `YamlFuncExtension` class within the `yaml_func_extension.py` file. You can refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When `agentUniverse` loads this configuration:
   - It parses the `@FUNC` annotation.
   - Executes the `load_api_key` function with the corresponding parameters.
   - Replaces the annotation content with the function's return value.

## 2. Environment Setup
In the example YAML, model keys and other parameters are configured using environment variable placeholders. The following section will introduce methods for setting environment variables.

Must be configured: `MISTRAL_API_KEY`
Optional: `MISTRAL_API_BASE` (default `https://api.mistral.ai/v1`), `MISTRAL_PROXY`

### 2.1 Configure through Python code
```python
import os
os.environ['MISTRAL_API_KEY'] = 'xxx'
os.environ['MISTRAL_API_BASE'] = 'https://api.mistral.ai/v1'
```

### 2.2 Configure through the configuration file
In the `custom_key.toml` file under the config directory of the project, add the configuration:
```toml
MISTRAL_API_KEY="xxx"
MISTRAL_API_BASE="https://api.mistral.ai/v1"
MISTRAL_PROXY=""
```

## 3. Obtaining the Mistral API KEY
Please refer to the official documentation of Mistral AI: https://console.mistral.ai/api-keys

## 4. Tips
In agentUniverse, the example `mistral_llm.yaml.example` is provided. Copy it to `mistral_llm.yaml`, configure your `MISTRAL_API_KEY`, and then resolve the `mistral_llm` component directly.
