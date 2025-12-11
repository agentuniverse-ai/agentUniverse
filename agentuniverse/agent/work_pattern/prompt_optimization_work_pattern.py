from typing import Optional, List, Dict

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.prompt_exec_agent_template import PromptExecAgentTemplate
from agentuniverse.agent.template.prompt_feedback_agent_template import PromptFeedbackAgentTemplate
from agentuniverse.agent.template.prompt_scoring_agent_template import PromptScoringAgentTemplate
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern


class PromptOptimizationWorkPattern(WorkPattern):
    executing: PromptExecAgentTemplate = None
    scoring: PromptScoringAgentTemplate = None
    feedback: PromptFeedbackAgentTemplate = None

    def invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
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

        for it in range(max_iterations):
            batch_list = self._make_batches(samples, batch_size)
            iteration_records: List[Dict] = []

            for batch in batch_list:
                qa_list: List[Dict] = []
                for q in batch:
                    exec_io = InputObject({"input": q})
                    exec_out: OutputObject = self.executing.run(**exec_io.to_dict())
                    answer = exec_out.get_data("output")
                    qa_list.append({"question": q, "answer": answer})

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
            fb_io = InputObject({"current_prompt": current_prompt, "evaluation_results": feedback_input})
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

        for it in range(max_iterations):
            batch_list = self._make_batches(samples, batch_size)
            iteration_records: List[Dict] = []

            for batch in batch_list:
                qa_list: List[Dict] = []
                for q in batch:
                    exec_io = InputObject({"input": q})
                    exec_out: OutputObject = await self.executing.async_run(**exec_io.to_dict())
                    answer = exec_out.get_data("output")
                    qa_list.append({"question": q, "answer": answer})

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
            fb_io = InputObject({"current_prompt": current_prompt, "evaluation_results": feedback_input})
            fb_out: OutputObject = await self.feedback.async_run(**fb_io.to_dict())
            next_prompt = fb_out.get_data("output") or current_prompt
            current_prompt = next_prompt
            self._set_executing_prompt(current_prompt)

        return {"result": result_iterations}

    def _validate_members(self):
        if self.executing and not isinstance(self.executing, AgentTemplate):
            raise ValueError(f"{self.executing} is not of the expected type AgentTemplate.")
        if self.scoring and not isinstance(self.scoring, PromptScoringAgentTemplate):
            raise ValueError(f"{self.scoring} is not of the expected type PromptScoringAgentTemplate.")
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

    def set_by_agent_model(self, **kwargs):
        inst = self.__class__()
        inst.name = self.name
        inst.description = self.description
        for key in ["executing", "scoring", "feedback"]:
            if key in kwargs:
                setattr(inst, key, kwargs[key])
        return inst
