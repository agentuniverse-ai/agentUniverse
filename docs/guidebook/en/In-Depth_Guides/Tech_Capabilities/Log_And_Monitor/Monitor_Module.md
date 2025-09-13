# Monitor Module

The agentUniverse monitor module focuses primarily on tracking and recording the LLM invocation and token expenses during the agent's runtime. In this document, we will provide a detailed introduction on how to utilize the LLM and agent invocation tracking capabilities that are currently available in agentUniverse.

## Monitor Configuration

Configure the settings for the monitor module in the main configuration file`config.toml` oof agentUniverse as follows:

```toml
[MONITOR]
activate = true
dir = './monitor'
```

- **`activate`**: The master switch for the monitor module is set tooff by default. When set to true, it will activate the LLM and agent invocation tracking functions.
- **`dir`**: The local storage directory for the monitor module, by default, is the 'monitor' directory located one level above the runtime directory. Users can customize the path of this directory.

### LLM Tracing Configuration

For the LLM invocation tracking capability in agentUniverse, the framework supports model granularity configuration. Once the main switch of the monitor module is activated, the invocation tracking function for specific models can be selectively disabled through the corresponding YAML file for the LLM.

For instance, if you have a user-defined model named demo_llm and you set the tracing option to false in its YAML configuration, the invocation tracking function for this model will be deactivated.

```yaml
name: 'demo_llm'
description: 'demo openai'
model_name: 'gpt-4o'
max_tokens: 1000
max_retries: 2
tracing: false
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.default_openai_llm'
  class: 'DefaultOpenAILLM'
```

**Special note:** In the main configuration file (config.toml) of agentUniverse, the master switch for the monitor module has the highest priority. If the activate configuration is set to false, any model granularity configurations will not take effect.

### Agent Tracing Configuration

FFor the agent invocation tracking capability, agentUniverse also supports agent-granularity configuration. Once the main
switch of the monitor module is activated, the invocation tracking function for specific agents can be selectively disabled through the corresponding YAML file for each agent.

For instance, for a user-defined agent named demo_agent, if the tracing is set to false in its YAML configuration, the invocation tracking function for this agent will be deactivated.

```yaml
info:
  name: 'demo_agent'
  description: 'demo agent'
profile:
  tracing: false
  prompt_version: demo_agent_prompt.cn
  llm_model:
    name: 'qwen_llm'
action:
  tool:
    - 'google_search_tool'
memory:
  name: ''
metadata:
  type: 'AGENT'
  module: 'sample_standard_app.intelligence.agentic.agent.agent_instance.demo_agent'
  class: 'DemoAgent'
```

**Special note:** In the main configuration file of agentUniverse, the master switch for the monitor module holds the highest priority. If the activate configuration option is set to false, any agent-granularity configurations will not take effect.


## Monitor Module Introduction

### LLM Invocation Tracking

If the user utilizes the **default model class** supported by agentUniverse, the feature can be enabled after the configuration, as described above, is completed.

#### trace_llm Decorator

If a user customizes an extension based on the agentUniverse's model base class LLM to implement a custom model invocation, it is necessary to add the @trace_llm decorator to the call/acall method of the custom model class.
Custom model example code as follows:

```python
from typing import Any, Iterator, Union, AsyncIterator

from agentuniverse.llm.llm import LLM, LLMOutput
from agentuniverse.base.annotation.trace import trace_llm


class DemoLLM(LLM):

    @trace_llm
    def call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        pass

    @trace_llm
    async def acall(self, *args: Any, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        pass
```

agentUniverse implements the `@trace_llm` decorator. When an agent calls the corresponding call/acall methods of the LLM, this decorator collects the model's prompt and response, serializes the information into JSON format, and stores it in the local storage directory corresponding to the monitor configuration. The data is stored in the form of jsonl files, divided by the hour.

#### Demo Effect

When calling the `demo_rag_agent` in the sample project of agentUniverse, using the gpt-4omodel with a query to analyze the reasons behind Warren Buffett's reduction of his stake in BYD, the model invocation tracking function captures the following data:

```json
{
  "source": "DefaultOpenAILLM.acall",
  "date": "2024-06-24 16:27:14",
  "llm_input": {
    "messages": [
      {
        "role": "system",
        "content": "You are an AI assistant proficient in information analysis.\nYour goal is to determine whether the corresponding answers to the questions provide valuable information, and to make suggestions and evaluations on the answers to the questions."
      },
      {
        "role": "user",
        "content": "The rules you need to follow are:\n1. You must answer the user's questions using English, combining the background information of the query with the knowledge you possess.\n2. Generate structured answers, and use blank lines to enhance the reading experience when necessary.\\n the question needs to be answered is: the reasons behind Warren Buffett's reduction of his stake in BYD\\n"
      }
    ]
  },
  "kwargs": {
    "model": "gpt-4o",
    "stream": false,
    "n": 1,
    "temperature": 0.5,
    "max_tokens": 1000
  },
  "llm_output": "Reasons Behind Warren Buffett's Reduction of His Stake in BYD\n\nWarren Buffett, through his company Berkshire Hathaway, has been reducing his stake in BYD since August 24, 2022. There are several potential reasons behind this decision:\n\n1. **Portfolio Rebalancing**:\n   - **Investment Strategy**: Buffett is known for his long-term investment strategy and value investing. Reducing his stake in BYD could be part of a broader portfolio rebalancing effort to diversify or allocate capital to other investment opportunities.\n   - **Profit Realization**: Given that Buffett's initial investment in BYD has appreciated significantly (approximately 31 times the initial value), selling some shares allows him to realize substantial profits.\n\n2. **Market Conditions**:\n   - **Stock Performance**: Despite the reduction in stake, BYD's stock price has remained relatively stable. This suggests that Buffett's decision to sell shares is not necessarily a reflection of a negative outlook on the company's stock performance.\n   - **Economic Factors**: The broader economic environment, including interest rates, inflation, and market volatility, may influence investment decisions. Buffett might be adjusting his holdings in response to these macroeconomic factors.\n\n3. **Company Evaluation**:\n   - **Intrinsic Value**: Buffett's investment philosophy focuses on the intrinsic value of a company rather than short-term stock price movements. He might believe that the current market price of BYD reflects its intrinsic value, prompting a partial exit.\n   - **Sector Analysis**: While BYD remains a leading player in the Chinese electric vehicle (EV) market, Buffett might be evaluating the competitive landscape and future growth prospects, leading to a strategic reduction in holdings.\n\n"
}
```

- **`source`**: the source of LLM invocation during agent runtime.
- **`date`**: LLM invocation time
- **`llm_input`**: The messages and model parameters used for the LLM invocation.
- **`llm_output`**: The text output by the LLM.


### Agent Invocation Tracking

#### trace_agent Decorator

agentUniverse implements the `@trace_agent` decorator. When an agent calls its run method, this decorator collects the agent's input and output parameters, serializes the information into JSON format, and stores it in the local storage directory that corresponds to the monitor configuration. The data is stored in the form of jsonl files, divided by both the hour and the specific agent.

#### Demo Effect

When you call the `demo_rag_agent`  in the sample project of agentUniverse, using the gpt-4o model with a query to analyze the reasons behind Warren Buffett's reduction of his stake in BYD, the agent invocation tracking function captures the following data:

```json
{
  "source": "demo_rag_agent", 
  "date": "2024-06-28 12:12:17", 
  "agent_input": {
    "kwargs": {
      "input": "analyze the reasons behind Warren Buffett's reduction of his stake in BYD"
    }
  }, 
  "agent_output": {
    "chat_history": [
      {
        "content": "analyze the reasons behind Warren Buffett's reduction of his stake in BYD", 
        "type": "human"
      }, 
      {
        "content": "### Analysis of Warren Buffett's Reduction in Stake in BYD\n\nWarren Buffett, through his investment conglomerate Berkshire Hathaway, has been gradually reducing his stake in BYD Company Limited, a major player in the electric vehicle (EV) market. Here are the key reasons behind this strategic move:\n\n#### 1. Profit-Taking\n\n**Initial Investment vs. Current Valuation:**\n- **Initial Investment:** Berkshire Hathaway first bought about 225 million shares of Shenzhen-based BYD in 2008.\n- **Current Sale:** Recently, Berkshire sold nearly 2.02 million Hong Kong-listed shares of BYD at $234.57 apiece.\n\nGiven the significant appreciation in the value of BYD shares since the initial investment, it is plausible that Berkshire Hathaway is looking to realize profits from this long-term investment.\n\n#### 2. Portfolio Management\n\n**Stake Reduction:**\n- **Previous Stake:** Berkshire Hathaway's stake in BYD was previously 7%.\n- **Current Stake:** The sale has reduced the stake to 5.99%.\n\nReducing the stake in BYD allows Berkshire Hathaway to prune its portfolio, potentially reallocating resources to other investment opportunities or maintaining a diversified portfolio.\n\n#### 3. Market Performance and Strategic Positioning\n\n**Market Analysis:**\n- BYD, along with Tesla, is a leading player in the global electric vehicle market. However, market dynamics and competition are constantly evolving. Berkshire Hathaway's decision to reduce its stake could be influenced by an analysis of market performance and future growth prospects.\n\n**Value Investing:**\n- Warren Buffett is known for his value investing strategy. The timing of the BYD share sale may align with Buffett's assessment of the company's current valuation relative to its future growth potential.\n\n### Conclusion\n\nWarren Buffett's reduction in his stake in BYD appears to be a strategic decision influenced by multiple factors, including profit-taking, portfolio management, and an analysis of market performance. This move aligns with Berkshire Hathaway's broader investment strategy and reflects a calculated approach to managing its investments in a dynamic global market.", 
        "type": "ai"
      }],
    "background": "Warren Buffett's Berkshire Hathaway may have sold BYD to take profits, free up cash, prune its portfolio, cut its geopolitical risk, ... Missing: analyze | Show results with:analyze. Explore Berkshire Hathaway's gradual divestment from BYD, analyzing geopolitical tensions, market performance, and strategic positioning. According to various media reports and analysis, Warren Buffett's reduction of shareholdings in BYD Company Limited may be due to various ... Berkshire sold nearly 2.02 million Hong Kong-listed shares of BYD at $234.57 apiece, dropping its stake from 6.18% to 5.99%. The disposal was ... Warren Buffett's Berkshire Hathaway has further cut its large stake in BYD, which vies with Tesla as the world's largest electric car (EV) maker ... Missing: analyze | Show results with:analyze. The sale reduced Berkshire's holding to 6.9%, from 7%. The conglomerate first bought about 225 million shares of Shenzhen-based BYD in 2008 for ... According to HKEX disclosure, Warren Buffett's investment flagship Berkshire Hathaway reduced its stake in BYD COMPANY (01211. Warren Buffett's Berkshire Hathaway Inc. (NYSE:BRK)(NYSE:BRK) is reducing its stake in BYD Co., Ltd. (OTC:BYDDY) (OTC:BYDDF) to less than 6%. The odd timing of the BYD share sale has less to do with Buffett's outlook on the Chinese EV maker and more to do with 'value investing.' Investment mogul Warren Buffett has quickened the reduction of his stake in Chinese electric vehicle-maker BYD, selling holdings in the firm ...", 
    "date": "2024-06-28", 
    "input": "analyze the reasons behind Warren Buffett's reduction of his stake in BYD", 
    "output": "### Analysis of Warren Buffett's Reduction in Stake in BYD\n\nWarren Buffett, through his investment conglomerate Berkshire Hathaway, has been gradually reducing his stake in BYD Company Limited, a major player in the electric vehicle (EV) market. Here are the key reasons behind this strategic move:\n\n#### 1. Profit-Taking\n\n**Initial Investment vs. Current Valuation:**\n- **Initial Investment:** Berkshire Hathaway first bought about 225 million shares of Shenzhen-based BYD in 2008.\n- **Current Sale:** Recently, Berkshire sold nearly 2.02 million Hong Kong-listed shares of BYD at $234.57 apiece.\n\nGiven the significant appreciation in the value of BYD shares since the initial investment, it is plausible that Berkshire Hathaway is looking to realize profits from this long-term investment.\n\n#### 2. Portfolio Management\n\n**Stake Reduction:**\n- **Previous Stake:** Berkshire Hathaway's stake in BYD was previously 7%.\n- **Current Stake:** The sale has reduced the stake to 5.99%.\n\nReducing the stake in BYD allows Berkshire Hathaway to prune its portfolio, potentially reallocating resources to other investment opportunities or maintaining a diversified portfolio.\n\n#### 3. Market Performance and Strategic Positioning\n\n**Market Analysis:**\n- BYD, along with Tesla, is a leading player in the global electric vehicle market. However, market dynamics and competition are constantly evolving. Berkshire Hathaway's decision to reduce its stake could be influenced by an analysis of market performance and future growth prospects.\n\n**Value Investing:**\n- Warren Buffett is known for his value investing strategy. The timing of the BYD share sale may align with Buffett's assessment of the company's current valuation relative to its future growth potential.\n\n### Conclusion\n\nWarren Buffett's reduction in his stake in BYD appears to be a strategic decision influenced by multiple factors, including profit-taking, portfolio management, and an analysis of market performance. This move aligns with Berkshire Hathaway's broader investment strategy and reflects a calculated approach to managing its investments in a dynamic global market."
  }
}
```

- **`source`**: the Agent name.
- **`date`**: Agent invocation time
- **`llm_input`**: Agent invocation input parameters
- **`llm_output`**: Agent output parameters