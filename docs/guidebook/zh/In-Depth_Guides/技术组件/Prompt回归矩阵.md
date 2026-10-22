# Prompt 离线回归矩阵

通过真实 PromptConfiger、PromptManager、Agent.process_prompt 继承、ChatPrompt 与 LangChain 消息渲染生成 golden 快照。不调用 LLM，不评价模型输出质量。

JSON 夹具结构：`{"version":1,"prompts":[{"path":"prompts/demo/v1.yaml"}],"cases":[{"id":"zh","profile":{"prompt_version":"demo.v1"},"inputs":{},"bindings":{"name":"小明"}}]}`。Prompt YAML 文件使用真实 instruction 等字段和 metadata.version，路径相对于夹具。

显式批准基线：`python -X utf8 -m agentuniverse.prompt.regression_matrix fixture.json golden.json --update`。
普通只读检查：`python -X utf8 -m agentuniverse.prompt.regression_matrix fixture.json golden.json`。

缺失基线不会自动生成；差异或渲染失败返回退出码1。缺变量、缺版本、渲染异常会报告状态，失败结果不能写成基线。只有 --update 才以临时文件替换指定基线，不能覆盖夹具或Prompt文件。提交前应检查差异。

profile 支持 introduction、target、instruction、prompt_version，遵循真实Agent继承优先级；inputs 支持 expert_framework、image_urls、audio_url；bindings 是文本模板变量。HTTP(S)媒体作为多模态消息保留但不下载，本地媒体路径拒绝，不验证远端媒体内容。

CLI 只支持内置Prompt的字面量YAML，拒绝自定义类、动态环境/FUNC表达式、重复键。不会模拟任意应用引导。API `render_matrix` 可使用专用测试进程中的稳定PromptManager；输入和注册对象不变。CLI临时注册并在结束恢复注册表，不应与真实应用并发修改注册表。

快照和diff会包含完整渲染内容，只使用用户批准的合成或可分享夹具。异常只报告类型。文件、case数和输出大小有界；完整格式及限制见英文 Prompt_Regression_Matrix.md。
