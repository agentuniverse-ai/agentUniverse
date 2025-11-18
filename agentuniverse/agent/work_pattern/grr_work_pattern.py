from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.critique_agent_template import CritiqueAgentTemplate
from agentuniverse.agent.template.generate_agent_template import GenerateAgentTemplate
from agentuniverse.agent.template.rewrite_agent_template import RewriteAgentTemplate
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern
from agentuniverse.base.util.logging.general_logger import Logger


class GrrWorkPattern(WorkPattern):
    generate: GenerateAgentTemplate = None
    critique: CritiqueAgentTemplate = None
    rewrite: RewriteAgentTemplate = None

    def invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        self._validate_work_pattern_members()

        grr_result = []
        max_critique_count = work_pattern_input.get("max_critique_count", 3)
        
        # 初始生成
        generate_result: OutputObject = self._invoke_generate(input_object, work_pattern_input)
        if not generate_result:
            Logger.error("GrrWorkPattern: generate result is empty")
            return {"result": grr_result}

        current_content = generate_result.to_dict().get("generate_result", "")
        
        for attempt in range(max_critique_count):
            grr_round_results = {"attempt": attempt + 1, "generate_result": generate_result}

            # critique
            critique_input = work_pattern_input.copy()
            critique_input["draft"] = current_content
            critique_result: OutputObject = self._invoke_critique(input_object, critique_input)
            grr_round_results["critique_result"] = critique_result.to_dict().get("critique_result", "")
            
            if not critique_result or not critique_result.to_dict().get("critique_result"):
                # 如果没有问题，结束循环
                grr_result.append(grr_round_results)
                break

            if critique_result.to_dict().get("score") >= 8:
                grr_result.append(grr_round_results)
                break
                
            # 进行重写
            rewrite_input = work_pattern_input.copy()
            rewrite_input["rewrite_input"] = current_content

            critique_result = critique_result.get_data("critique_result", {})

            rewrite_input["critique"] = critique_result.get("critique", "")
            rewrite_input["suggestion"] = critique_result.get("suggestion", "")
            rewrite_input["score"] = critique_result.get("score", "")

            rewrite_result: OutputObject = self._invoke_rewrite(input_object, rewrite_input)
            grr_round_results["rewrite_result"] = rewrite_result.to_dict().get("rewrite_result", "")
            rewrite_result: dict = self._invoke_rewrite(input_object, rewrite_input).to_dict()

            grr_round_results["rewrite_result"] = rewrite_result.get("rewrite_result", "")
            
            # 更新当前内容
            if rewrite_result and rewrite_result.get("rewrite_result"):
                current_content = rewrite_result.get("rewrite_result")
            
            grr_result.append(grr_round_results)
            
        return {"result": grr_result, "final_content": current_content}

    async def async_invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        self._validate_work_pattern_members()

        grr_result = []
        max_critique_count = work_pattern_input.get("max_critique_count", 3)
        
        # 初始生成
        generate_result = await self._async_invoke_generate(input_object, work_pattern_input)
        if not generate_result:
            return {"result": grr_result}
            
        current_content = generate_result.get("content", "")
        
        for attempt in range(max_critique_count):
            grr_round_results = {"attempt": attempt + 1}
            
            # 记录生成结果
            grr_round_results["generate_result"] = generate_result
            
            # 进行批评
            critique_input = work_pattern_input.copy()
            critique_input["content"] = current_content
            critique_result = await self._async_invoke_critique(input_object, critique_input)
            grr_round_results["critique_result"] = critique_result
            
            if not critique_result or not critique_result.get("issues"):
                # 如果没有问题，结束循环
                grr_result.append(grr_round_results)
                break
                
            # 进行重写
            rewrite_input = work_pattern_input.copy()
            rewrite_input["content"] = current_content
            rewrite_input["critique"] = critique_result.get("issues", "")
            rewrite_result = await self._async_invoke_rewrite(input_object, rewrite_input)
            grr_round_results["rewrite_result"] = rewrite_result
            
            # 更新当前内容
            if rewrite_result and rewrite_result.get("improved_content"):
                current_content = rewrite_result.get("improved_content")
            
            grr_result.append(grr_round_results)
            
        return {"result": grr_result, "final_content": current_content}

    def _invoke_generate(self, input_object: InputObject, work_pattern_input: dict):
        if not self.generate:
            return None
        generate_input = input_object.to_dict()
        generate_input.update(work_pattern_input)
        return self.generate.run(**generate_input)

    def _invoke_critique(self, input_object: InputObject, critique_input: dict):
        if not self.critique:
            return None
        critique_input_dict = input_object.to_dict()
        critique_input_dict.update(critique_input)
        return self.critique.run(**critique_input_dict)

    def _invoke_rewrite(self, input_object: InputObject, rewrite_input: dict):
        if not self.rewrite:
            return None
        rewrite_input_dict = input_object.to_dict()
        rewrite_input_dict.update(rewrite_input)
        return self.rewrite.run(**rewrite_input_dict)

    async def _async_invoke_generate(self, input_object: InputObject, work_pattern_input: dict):
        if not self.generate:
            return None
        generate_input = input_object.to_dict()
        generate_input.update(work_pattern_input)
        return await self.generate.async_run(**generate_input)

    async def _async_invoke_critique(self, input_object: InputObject, critique_input: dict):
        if not self.critique:
            return None
        critique_input_dict = input_object.to_dict()
        critique_input_dict.update(critique_input)
        return await self.critique.async_run(**critique_input_dict)

    async def _async_invoke_rewrite(self, input_object: InputObject, rewrite_input: dict):
        if not self.rewrite:
            return None
        rewrite_input_dict = input_object.to_dict()
        rewrite_input_dict.update(rewrite_input)
        return await self.rewrite.async_run(**rewrite_input_dict)

    def set_by_agent_model(self, **kwargs):
        grr_work_pattern_instance = self.__class__()
        grr_work_pattern_instance.name = self.name
        grr_work_pattern_instance.description = self.description
        for key in ['generate', 'critique', 'rewrite']:
            if key in kwargs:
                setattr(grr_work_pattern_instance, key, kwargs[key])
        return grr_work_pattern_instance

    def _validate_work_pattern_members(self):
        if self.generate and not isinstance(self.generate, GenerateAgentTemplate):
            raise ValueError(f"{self.generate} is not of the expected type GenerateAgentTemplate.")
        if self.critique and not isinstance(self.critique, CritiqueAgentTemplate):
            raise ValueError(f"{self.critique} is not of the expected type CritiqueAgentTemplate.")
        if self.rewrite and not isinstance(self.rewrite, RewriteAgentTemplate):
            raise ValueError(f"{self.rewrite} is not of the expected type RewriteAgentTemplate.")



