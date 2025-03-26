# GLM 使用
## 1. 创建相关文件
创建一个yaml文件，例如 user_glm.yaml
将以下内容粘贴到您的user_glm.yaml文件当中
```yaml
name: 'user_zhipu_llm'
description: 'default default_zhipu_llm llm with spi'
model_name: 'glm-4-flash'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${ZHIPU_API_KEY}'
api_base: '${ZHIPU_API_BASE}'
organization: '${ZHIPU_ORGANIZATION}'
proxy: '${ZHIPU_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.zhipu_openai_style_llm'
  class: 'DefaultZhiPuLLM'
```

**note:** api_key/api_base/organization/proxy等模型参数有三种配置方法

1. 直接字符串值：直接在配置文件中输入API密钥字符串。

    ```yaml
    api_key: 'sk-***'
    ```

2. 环境变量占位符：使用${VARIABLE_NAME}语法从环境变量中加载。当agentUniverse启动时，会自动从环境变量读取相应的值。
    ```yaml
    api_key: '${ZHIPU_API_KEY}'
    ```
   
3. 自定义函数加载：使用@FUNC注解在运行时通过自定义函数动态加载API密钥。
    ```yaml
    api_key: '@FUNC(load_api_key(model_name="zhipu"))'
    ```
    该函数需要在yaml_func_extension.py文件的YamlFuncExtension类中定义，可参考样例工程中的[YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)，当agentUniverse加载此配置时：
   - 解析@FUNC注解
   - 执行load_api_key函数并传入相应参数
   - 用函数返回值替换注解内容
   

## 2. 环境设置
示例yaml中模型密钥等参数使用环境变量占位符，下面将介绍环境变量设置方法。

必须配置：ZHIPU_API_KEY
可选配置：ZHIPU_API_BASE, ZHIPU_PROXY, ZHIPU_ORGANIZATION
### 2.1 通过python代码配置
```python
import os
os.environ['ZHIPU_API_KEY'] = '*****'
os.environ['ZHIPU_API_BASE'] = 'xxxxx'
```
### 2.2 通过配置文件配置
在项目的config目录下的custom_key.toml当中，添加配置：
```toml
ZHIPU_API_KEY='xxxxxx'
ZHIPU_API_BASE='https://open.bigmodel.cn/api/paas/v4/'
ZHIPU_PROXY=''
ZHIPU_ORGANIZATION=''
```
## 3.ZHIPU API KEY 获取
参考 智谱GLM 官方文档：https://maas.aminer.cn

## 4. Tips
在agentuniverse中，我们已经创建了一个name为default_zhipu_llm的llm,用户在配置ZHIPU_API_KEY、ZHIPU_API_BASE之后可以直接使用。



