from openai import OpenAI 
 
client = OpenAI( 
    api_key="sk-9fddc29cfd054c348ff93205985f08f7", 
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", 
) 
 
resp = client.chat.completions.create( 
    model="qwen-plus", 
    messages=[{"role": "user", "content": "保险产品A怎么升级"}], 
) 
 
print(resp) 
