import uuid
from typing import Optional, List, Dict, Union, Any

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.answer_agent_template import AnswerAgentTemplate
from agentuniverse.agent.template.feedback_agent_template import FeedbackAgentTemplate
from agentuniverse.agent.template.scoring_agent_template import ScoringAgentTemplate
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern


class OptimizationWorkPattern(WorkPattern):
    executing: AnswerAgentTemplate = None
    scoring: ScoringAgentTemplate = None
    feedback: FeedbackAgentTemplate = None

    def invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        self._validate_members()

        samples: List[Union[str, Dict[str, Any]]] = work_pattern_input.get("samples", []) or []
        batch_size: int = int(work_pattern_input.get("batch_size", 3))
        max_iterations: int = int(work_pattern_input.get("max_iterations", 5))
        avg_score_threshold: Optional[float] = work_pattern_input.get("avg_score_threshold")
        pass_rate_threshold: Optional[float] = work_pattern_input.get("pass_rate_threshold")
        pass_score: float = float(work_pattern_input.get("pass_score", 60))
        current_prompt: str = work_pattern_input.get("initial_prompt") or ""
        scoring_standard: str = work_pattern_input.get("scoring_standard") or ""
        agent_name_for_optimization: str = work_pattern_input.get("agent_name_for_optimization") or ""
        result_iterations: List[Dict] = []

        self._set_executing_prompt(current_prompt)
        session_id = uuid.uuid4().hex

        sample_index = 0
        total_sample_count = len(samples)

        for it in range(max_iterations):
            batch = []
            if total_sample_count > 0:
                for _ in range(batch_size):
                    batch.append(samples[sample_index % total_sample_count])
                    sample_index += 1
            
            batch_list = [batch] if batch else []
            iteration_records: List[Dict] = []

            for batch in batch_list:
                qa_list: List[Dict] = []
                for sample in batch:
                    # 获取executing agent的输入key列表
                    agent_input_keys = self.executing.input_keys() if hasattr(self.executing, 'input_keys') else ['input']
                    
                    # 使用智能方法构建agent输入
                    agent_input_dict = self._build_agent_input(sample, agent_input_keys)
                    
                    exec_io = InputObject(agent_input_dict)
                    exec_out: OutputObject = self.executing.run(**exec_io.to_dict())
                    answer = exec_out.get_data("output")
                    
                    # 保存原始sample和对应的answer，保持数据结构一致性
                    sample_str = str(sample) if not isinstance(sample, str) else sample
                    qa_list.append({"question": sample_str, "answer": answer})

                scored_items: List[Dict] = []
                for item in qa_list:
                    review_io = InputObject({"input": item["question"], "expressing_result": item["answer"],"scoring_standard": scoring_standard})
                    review_out: OutputObject = self.scoring.run(**review_io.to_dict())
                    score = review_out.get_data("score") or 0
                    reason = review_out.get_data("suggestion") or review_out.get_data("output")
                    scored_items.append({
                        "question": item["question"],
                        "answer": item["answer"],
                        "score": score,
                        "reason": reason
                    })

                avg_score = self._avg([x["score"] for x in scored_items])
                pass_rate = self._pass_rate([x["score"] for x in scored_items], pass_score)

                iteration_records.append({
                    "items": scored_items,
                    "avg_score": avg_score,
                    "pass_rate": pass_rate
                })

            stop = False
            stop_reason = ""
            if avg_score_threshold is not None:
                all_scores = [rec["avg_score"] for rec in iteration_records]
                if len(all_scores) > 0 and self._avg(all_scores) >= float(avg_score_threshold):
                    stop = True
                    stop_reason = "avg_score_threshold_met"
            if not stop and pass_rate_threshold is not None:
                all_rates = [rec["pass_rate"] for rec in iteration_records]
                if len(all_rates) > 0 and self._avg(all_rates) >= float(pass_rate_threshold):
                    stop = True
                    stop_reason = "pass_rate_threshold_met"

            result_iterations.append({
                "iteration": it + 1,
                "prompt": current_prompt,
                "batches": iteration_records,
                "stop_reason": stop_reason
            })

            if stop:
                break

            feedback_input = self._build_feedback_input(iteration_records)
            fb_io = InputObject({"current_prompt": current_prompt, "evaluation_results": feedback_input, "session_id": session_id})
            fb_out: OutputObject = self.feedback.run(**fb_io.to_dict())
            next_prompt = fb_out.get_data("output") or current_prompt
            current_prompt = next_prompt
            self._set_executing_prompt(current_prompt)

        return {"result": result_iterations}

    async def async_invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        self._validate_members()

        samples: List[str] = work_pattern_input.get("samples", []) or []
        batch_size: int = int(work_pattern_input.get("batch_size", 3))
        max_iterations: int = int(work_pattern_input.get("max_iterations", 5))
        avg_score_threshold: Optional[float] = work_pattern_input.get("avg_score_threshold")
        pass_rate_threshold: Optional[float] = work_pattern_input.get("pass_rate_threshold")
        pass_score: float = float(work_pattern_input.get("pass_score", 60))
        current_prompt: str = work_pattern_input.get("initial_prompt") or ""
        scoring_standard: str = work_pattern_input.get("scoring_standard") or ""
        result_iterations: List[Dict] = []

        self._set_executing_prompt(current_prompt)
        session_id = uuid.uuid4().hex

        sample_index = 0
        total_sample_count = len(samples)

        for it in range(max_iterations):
            batch = []
            if total_sample_count > 0:
                for _ in range(batch_size):
                    batch.append(samples[sample_index % total_sample_count])
                    sample_index += 1
            
            batch_list = [batch] if batch else []
            iteration_records: List[Dict] = []

            for batch in batch_list:
                qa_list: List[Dict] = []
                for sample in batch:
                    # 获取executing agent的输入key列表
                    agent_input_keys = self.executing.input_keys() if hasattr(self.executing, 'input_keys') else ['input']
                    
                    # 使用智能方法构建agent输入
                    agent_input_dict = self._build_agent_input(sample, agent_input_keys)
                    
                    exec_io = InputObject(agent_input_dict)
                    exec_out: OutputObject = await self.executing.async_run(**exec_io.to_dict())
                    answer = exec_out.get_data("output")
                    
                    # 保存原始sample和对应的answer，保持数据结构一致性
                    sample_str = str(sample) if not isinstance(sample, str) else sample
                    qa_list.append({"question": sample_str, "answer": answer})

                scored_items: List[Dict] = []
                for item in qa_list:
                    review_io = InputObject({"input": item["question"], "expressing_result":  item["answer"],"scoring_standard": scoring_standard})
                    review_out: OutputObject = await self.scoring.async_run(**review_io.to_dict())
                    score = review_out.get_data("score") or 0
                    reason = review_out.get_data("suggestion") or review_out.get_data("output")
                    scored_items.append({
                        "question": item["question"],
                        "answer": item["answer"],
                        "score": score,
                        "reason": reason
                    })

                avg_score = self._avg([x["score"] for x in scored_items])
                pass_rate = self._pass_rate([x["score"] for x in scored_items], pass_score)

                iteration_records.append({
                    "items": scored_items,
                    "avg_score": avg_score,
                    "pass_rate": pass_rate
                })

            stop = False
            stop_reason = ""
            if avg_score_threshold is not None:
                all_scores = [rec["avg_score"] for rec in iteration_records]
                if len(all_scores) > 0 and self._avg(all_scores) >= float(avg_score_threshold):
                    stop = True
                    stop_reason = "avg_score_threshold_met"
            if not stop and pass_rate_threshold is not None:
                all_rates = [rec["pass_rate"] for rec in iteration_records]
                if len(all_rates) > 0 and self._avg(all_rates) >= float(pass_rate_threshold):
                    stop = True
                    stop_reason = "pass_rate_threshold_met"

            result_iterations.append({
                "iteration": it + 1,
                "prompt": current_prompt,
                "batches": iteration_records,
                "stop_reason": stop_reason
            })

            if stop:
                break

            feedback_input = self._build_feedback_input(iteration_records)
            fb_io = InputObject({"current_prompt": current_prompt, "evaluation_results": feedback_input, "session_id": session_id})
            fb_out: OutputObject = await self.feedback.async_run(**fb_io.to_dict())
            next_prompt = fb_out.get_data("output") or current_prompt
            current_prompt = next_prompt
            self._set_executing_prompt(current_prompt)

        return {"result": result_iterations}

    def _validate_members(self):
        if self.executing and not isinstance(self.executing, AgentTemplate):
            raise ValueError(f"{self.executing} is not of the expected type AgentTemplate.")
        if self.scoring and not isinstance(self.scoring, ScoringAgentTemplate):
            raise ValueError(f"{self.scoring} is not of the expected type ScoringAgentTemplate.")
        if self.feedback and not isinstance(self.feedback, AgentTemplate):
            raise ValueError(f"{self.feedback} is not of the expected type AgentTemplate.")

    def _set_executing_prompt(self, prompt_text: str):
        if not self.executing:
            return
        if prompt_text:
            self.executing.prompt_version = None
            if isinstance(self.executing.agent_model.profile, dict):
                self.executing.agent_model.profile["prompt_version"] = None
                self.executing.agent_model.profile["instruction"] = prompt_text

    def _make_batches(self, samples: List[str], batch_size: int) -> List[List[str]]:
        batches: List[List[str]] = []
        if batch_size <= 0:
            batch_size = 1
        for i in range(0, len(samples), batch_size):
            batches.append(samples[i:i + batch_size])
        return batches

    def _avg(self, nums: List[float]) -> float:
        if not nums:
            return 0.0
        return float(sum(nums) / len(nums))

    def _pass_rate(self, nums: List[float], pass_score: float) -> float:
        if not nums:
            return 0.0
        passed = [n for n in nums if n >= pass_score]
        return float(len(passed) / len(nums))

    def _build_feedback_input(self, iteration_records: List[Dict]) -> str:
        merged: List[Dict] = []
        for rec in iteration_records:
            merged.extend(rec.get("items", []))
        return str(merged)

    def _build_agent_input(self, sample: Union[str, Dict[str, Any]], agent_input_keys: List[str]) -> Dict[str, Any]:
        """
        根据sample格式和agent的输入key构建agent输入字典
        
        Args:
            sample: 样本数据，可以是字符串或字典
            agent_input_keys: agent期望的输入key列表
            
        Returns:
            构建好的输入字典
        """
        if isinstance(sample, str):
            # 简单字符串格式：使用第一个输入key
            primary_key = agent_input_keys[0] if agent_input_keys else 'input'
            return {primary_key: sample}
        elif isinstance(sample, dict):
            # 字典格式：智能匹配agent的输入key
            agent_input = {}
            
            # 首先尝试精确匹配所有的agent输入key
            for key in agent_input_keys:
                if key in sample:
                    agent_input[key] = sample[key]
            
            # 如果没有找到任何匹配，尝试模糊匹配
            if not agent_input:
                # 尝试常用key名称
                common_key_mappings = {
                    'input': ['input', 'question', 'query', 'text', 'content'],
                    'fund_info': ['fund_info', 'fund', 'fund_information'],
                    'planning_result': ['planning_result', 'plan', 'planning', 'strategy']
                }
                
                for agent_key in agent_input_keys:
                    possible_keys = common_key_mappings.get(agent_key, [agent_key])
                    for possible_key in possible_keys:
                        if possible_key in sample:
                            agent_input[agent_key] = sample[possible_key]
                            break
                    
                    # 如果还是没有找到，使用第一个可用的值
                    if agent_key not in agent_input and sample:
                        # 使用sample中的第一个值作为默认值
                        first_key = list(sample.keys())[0]
                        agent_input[agent_key] = sample[first_key]
                        
            # 如果agent_input仍然为空，使用第一个输入key和第一个sample值
            if not agent_input and agent_input_keys:
                first_agent_key = agent_input_keys[0]
                first_sample_value = list(sample.values())[0] if sample else ""
                agent_input[first_agent_key] = first_sample_value
                
            return agent_input
        else:
            # 其他格式：使用第一个输入key的字符串表示
            primary_key = agent_input_keys[0] if agent_input_keys else 'input'
            return {primary_key: str(sample)}

    def set_by_agent_model(self, **kwargs):
        """Set the optimization work pattern instance by agent model.
        
        Args:
            **kwargs: Keyword arguments containing agent instances.
            
        Returns:
            OptimizationWorkPattern: A new instance with agents configured.
        """
        optimization_work_pattern_instance = self.__class__()
        optimization_work_pattern_instance.name = self.name
        optimization_work_pattern_instance.description = self.description
        
        # Set the three core components of optimization work pattern
        for key in ['executing', 'scoring', 'feedback']:
            if key in kwargs:
                setattr(optimization_work_pattern_instance, key, kwargs[key])
        
        return optimization_work_pattern_instance
