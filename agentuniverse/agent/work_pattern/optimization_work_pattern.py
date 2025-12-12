import uuid
import os
import json
from typing import Optional, List, Dict, Union, Any
import itertools
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.answer_agent_template import AnswerAgentTemplate
from agentuniverse.agent.template.feedback_agent_template import FeedbackAgentTemplate
from agentuniverse.agent.template.scoring_agent_template import ScoringAgentTemplate
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern

class MemoryStore:
    def __init__(self, path: Optional[str] = None):
        self.path = path or os.path.expanduser("~/.agentuniverse/optimization_memory.json")
        self._data: Dict[str, List[Dict]] = self._load()

    def _load(self) -> Dict[str, List[Dict]]:
        try:
            if os.path.exists(self.path):
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def make_signature(self, samples: List[Union[str, Dict[str, Any]]]) -> str:
        tokens: List[str] = []
        for s in samples or []:
            text = s if isinstance(s, str) else json.dumps(s, ensure_ascii=False)
            tokens.extend([t.lower() for t in text.split()])
        return "|".join(sorted(set(tokens)))

    def retrieve(self, sample_sig: str) -> List[Dict]:
        return list(self._data.get(sample_sig, []))

    def append(self, sample_sig: str, record: Dict):
        self._data.setdefault(sample_sig, []).append(record)
        self._save()


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
        max_history_records: int = int(work_pattern_input.get("max_history_records", 5))
        max_feedback_chars: int = int(work_pattern_input.get("max_feedback_chars", 15000))
        current_prompt: str = work_pattern_input.get("initial_prompt") or ""
        scoring_standard: str = work_pattern_input.get("scoring_standard") or ""
        agent_name_for_optimization: str = work_pattern_input.get("agent_name_for_optimization") or ""
        result_iterations: List[Dict] = []

        self._set_executing_prompt(current_prompt)
        session_id = uuid.uuid4().hex
        memory_store = MemoryStore()
        sample_sig = memory_store.make_signature(samples)
        prior_insights = memory_store.retrieve(sample_sig)
        chat_history: List[Dict] = []
        
        # 从prior_insights初始化知识库
        knowledge_base = self._init_knowledge_base_from_insights(prior_insights, pass_score) if prior_insights else None
        
        # 从历史经验生成初始建议（可用于日志或未来增强）
        if prior_insights:
            initial_suggestions = self._synthesize_from_insights(prior_insights, pass_score)
            # 这里可以选择将suggestions融入initial_prompt或记录日志
            # 暂时仅作为knowledge_base的一部分存储

        batches: List[List[Union[str, Dict[str, Any]]]] = self._make_batches_itertools(samples, batch_size, max_iterations) if samples else []
        if not batches:
            return {"result": []}
        stop = False
        stop_reason = ""
        for it in range(max_iterations):
            iteration_records: List[Dict] = []
            batch = batches[it]
            qa_list: List[Dict] = []
            for sample in batch:
                agent_input_keys = self.executing.input_keys() if hasattr(self.executing, 'input_keys') else ['input']
                agent_input_dict = self._build_agent_input(sample, agent_input_keys)

                exec_io = InputObject(agent_input_dict)
                exec_out: OutputObject = self.executing.run(**exec_io.to_dict())
                answer = exec_out.get_data("output")

                sample_str = str(sample) if not isinstance(sample, str) else sample
                qa_list.append({"question": sample_str, "answer": answer})

            scored_items: List[Dict] = []
            for item in qa_list:
                review_io = InputObject({"input": item["question"], "expressing_result": item["answer"], "scoring_standard": scoring_standard})
                review_out: OutputObject = self.scoring.run(**review_io.to_dict())
                score = review_out.get_data("score") or 0
                reason = review_out.get_data("reason") or review_out.get_data("output")
                scored_items.append({
                    "question": item["question"],
                    "answer": item["answer"],
                    "score": score,
                    "reason": reason
                })

            avg_score = self._avg([x["score"] for x in scored_items])
            pass_rate = self._pass_rate([x["score"] for x in scored_items], pass_score)

            record = {
                "items": scored_items,
                "avg_score": avg_score,
                "pass_rate": pass_rate
            }
            iteration_records.append(record)

            if avg_score_threshold is not None and avg_score >= float(avg_score_threshold):
                stop = True
                stop_reason = "avg_score_threshold_met"
            if not stop and pass_rate_threshold is not None and pass_rate >= float(pass_rate_threshold):
                stop = True
                stop_reason = "pass_rate_threshold_met"

            feedback_input_dict = self._build_feedback_input(current_prompt, [record], pass_score, knowledge_base)
            history_summary = ""
            if len(chat_history)>0 and len(chat_history)<=max_history_records:
                # 使用智能筛选替代简单保留
                selected_history = self._select_important_records(chat_history, max_history_records, pass_score)
                history_summary = self._summarize_records(selected_history, pass_score)
            elif len(chat_history) > max_history_records:
                # 智能选择重要记录
                selected_history = self._select_important_records(chat_history, max_history_records, pass_score)
                # 对未选中的记录生成摘要
                unselected = [rec for rec in chat_history if rec not in selected_history]
                if unselected:
                    history_summary = self._summarize_records(unselected, pass_score)
            else:
                history_summary=""

            # 将结构化feedback与历史信息合并
            fb_payload = {
                **feedback_input_dict,  # 展开结构化的feedback输入
                "session_id": session_id,
                "history_summary": history_summary
            }
            fb_io = InputObject(fb_payload)
            fb_out: OutputObject = self.feedback.run(**fb_io.to_dict())
            next_prompt = fb_out.get_data("output") or current_prompt
            memory_store.append(sample_sig, {
                "prompt_before": current_prompt,
                "iteration": it + 1,
                "records": [record],
                "prompt_after": next_prompt
            })
            chat_history.append({
                "prompt": current_prompt,
                "batches": [record]
            })
            current_prompt = next_prompt
            self._set_executing_prompt(current_prompt)


            result_iterations.append({
                "iteration": it + 1,
                "prompt": current_prompt,
                "batches": iteration_records,
                "stop_reason": stop_reason
            })

            if stop:
                break

        return {"result": result_iterations}

    async def async_invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        self._validate_members()

        samples: List[Union[str, Dict[str, Any]]] = work_pattern_input.get("samples", []) or []
        batch_size: int = int(work_pattern_input.get("batch_size", 3))
        max_iterations: int = int(work_pattern_input.get("max_iterations", 5))
        avg_score_threshold: Optional[float] = work_pattern_input.get("avg_score_threshold")
        pass_rate_threshold: Optional[float] = work_pattern_input.get("pass_rate_threshold")
        pass_score: float = float(work_pattern_input.get("pass_score", 60))
        max_history_records: int = int(work_pattern_input.get("max_history_records", 8))
        max_feedback_chars: int = int(work_pattern_input.get("max_feedback_chars", 15000))
        current_prompt: str = work_pattern_input.get("initial_prompt") or ""
        scoring_standard: str = work_pattern_input.get("scoring_standard") or ""
        agent_name_for_optimization: str = work_pattern_input.get("agent_name_for_optimization") or ""
        result_iterations: List[Dict] = []

        self._set_executing_prompt(current_prompt)
        session_id = uuid.uuid4().hex
        memory_store = MemoryStore()
        sample_sig = memory_store.make_signature(samples)
        prior_insights = memory_store.retrieve(sample_sig)
        chat_history: List[Dict] = []
        
        # 从prior_insights初始化知识库
        knowledge_base = self._init_knowledge_base_from_insights(prior_insights, pass_score) if prior_insights else None
        
        # 从历史经验生成初始建议（可用于日志或未来增强）
        if prior_insights:
            initial_suggestions = self._synthesize_from_insights(prior_insights, pass_score)
            # 这里可以选择将suggestions融入initial_prompt或记录日志
            # 暂时仅作为knowledge_base的一部分存储

        batches: List[List[Union[str, Dict[str, Any]]]] = self._make_batches_itertools(samples, batch_size, max_iterations) if samples else []
        if not batches:
            return {"result": []}
        stop = False
        stop_reason = ""
        for it in range(max_iterations):
            iteration_records: List[Dict] = []
            batch = batches[it]
            qa_list: List[Dict] = []
            for sample in batch:
                agent_input_keys = self.executing.input_keys() if hasattr(self.executing, 'input_keys') else ['input']
                agent_input_dict = self._build_agent_input(sample, agent_input_keys)

                exec_io = InputObject(agent_input_dict)
                exec_out: OutputObject = await self.executing.async_run(**exec_io.to_dict())
                answer = exec_out.get_data("output")

                sample_str = str(sample) if not isinstance(sample, str) else sample
                qa_list.append({"question": sample_str, "answer": answer})

            scored_items: List[Dict] = []
            for item in qa_list:
                review_io = InputObject({"input": item["question"], "expressing_result": item["answer"], "scoring_standard": scoring_standard})
                review_out: OutputObject = await self.scoring.async_run(**review_io.to_dict())
                score = review_out.get_data("score") or 0
                reason = review_out.get_data("reason") or review_out.get_data("output")
                scored_items.append({
                    "question": item["question"],
                    "answer": item["answer"],
                    "score": score,
                    "reason": reason
                })

            avg_score = self._avg([x["score"] for x in scored_items])
            pass_rate = self._pass_rate([x["score"] for x in scored_items], pass_score)

            record = {
                "items": scored_items,
                "avg_score": avg_score,
                "pass_rate": pass_rate
            }
            iteration_records.append(record)

            if avg_score_threshold is not None and avg_score >= float(avg_score_threshold):
                stop = True
                stop_reason = "avg_score_threshold_met"
            if not stop and pass_rate_threshold is not None and pass_rate >= float(pass_rate_threshold):
                stop = True
                stop_reason = "pass_rate_threshold_met"

            feedback_input_dict = self._build_feedback_input(current_prompt, [record], pass_score, knowledge_base)
            history_summary = ""
            if len(chat_history)>0 and len(chat_history)<=max_history_records:
                # 使用智能筛选替代简单保留
                selected_history = self._select_important_records(chat_history, max_history_records, pass_score)
                history_summary = self._summarize_records(selected_history, pass_score)
            elif len(chat_history) > max_history_records:
                # 智能选择重要记录
                selected_history = self._select_important_records(chat_history, max_history_records, pass_score)
                # 对未选中的记录生成摘要
                unselected = [rec for rec in chat_history if rec not in selected_history]
                if unselected:
                    history_summary = self._summarize_records(unselected, pass_score)
            else:
                history_summary=""

            # 将结构化feedback与历史信息合并
            fb_payload = {
                **feedback_input_dict,  # 展开结构化的feedback输入
                "session_id": session_id,
                "history_summary": history_summary
            }
            fb_io = InputObject(fb_payload)
            fb_out: OutputObject = await self.feedback.async_run(**fb_io.to_dict())
            next_prompt = fb_out.get_data("output") or current_prompt
            memory_store.append(sample_sig, {
                "prompt_before": current_prompt,
                "iteration": it + 1,
                "records": [record],
                "prompt_after": next_prompt
            })
            chat_history.append({
                "prompt": current_prompt,
                "batches": [record]
            })
            current_prompt = next_prompt
            self._set_executing_prompt(current_prompt)


            result_iterations.append({
                "iteration": it + 1,
                "prompt": current_prompt,
                "batches": iteration_records,
                "stop_reason": stop_reason
            })

            if stop:
                break

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

    def _make_batches_itertools(self, samples: List[Union[str, Dict[str, Any]]], batch_size: int, max_iterations: int) -> List[List[Union[str, Dict[str, Any]]]]:
        """
        使用 itertools.cycle 实现循环批次生成。
        """
        if not samples or batch_size <= 0 or max_iterations <= 0:
            return []

        batches: List[List[Union[str, Dict[str, Any]]]] = []
        # 创建一个可以无限循环提供样本的迭代器
        sample_cycler = itertools.cycle(samples)

        for _ in range(max_iterations):
            # 从迭代器中取出 batch_size 个样本来组成一个批次
            batch = [next(sample_cycler) for _ in range(batch_size)]
            batches.append(batch)

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

    def _extract_knowledge(self, current_prompt: str, records: List[Dict], pass_score: float) -> Dict:
        """
        从评估结果中提取结构化知识
        
        Args:
            current_prompt: 当前使用的prompt
            records: 评估记录列表
            pass_score: 及格分数线
            
        Returns:
            结构化的知识字典，包含成功案例、失败案例、分数分布等
        """
        knowledge = {
            "successful_samples": [],
            "failed_samples": [],
            "score_distribution": {},
            "common_failure_reasons": {}
        }
        
        for rec in records:
            for item in rec.get("items", []):
                score = item.get("score", 0)
                
                entry = {
                    "question": item.get("question"),
                    "answer": item.get("answer"),
                    "score": score,
                    "reason": item.get("reason")
                }
                
                if score >= pass_score:
                    knowledge["successful_samples"].append(entry)
                else:
                    knowledge["failed_samples"].append(entry)
                    
                    # 统计失败原因
                    reason = item.get("reason", "unknown")
                    knowledge["common_failure_reasons"][reason] = \
                        knowledge["common_failure_reasons"].get(reason, 0) + 1
                
                # 分数分布统计
                score_bucket = int(score // 10) * 10  # 按10分区间统计
                bucket_key = f"{score_bucket}-{score_bucket + 10}"
                knowledge["score_distribution"][bucket_key] = \
                    knowledge["score_distribution"].get(bucket_key, 0) + 1
        
        return knowledge

    def _build_feedback_input(self, current_prompt: str, iteration_records: List[Dict], pass_score: float, 
                            knowledge_base: Optional[Dict] = None) -> Dict:
        """
        构建增强的feedback输入，包含结构化知识
        
        Args:
            current_prompt: 当前prompt
            iteration_records: 当前迭代的评估记录
            pass_score: 及格分数
            knowledge_base: 可选的历史知识库
            
        Returns:
            结构化的feedback输入字典
        """
        # 提取当前轮次的知识
        current_knowledge = self._extract_knowledge(current_prompt, iteration_records, pass_score)
        
        # 计算所有分数
        all_scores = []
        for rec in iteration_records:
            for item in rec.get("items", []):
                score = item.get("score")
                if score is not None:
                    all_scores.append(score)
        
        # 构建结构化输入
        feedback_input = {
            "current_prompt": current_prompt,
            "current_performance": {
                "avg_score": self._avg(all_scores) if all_scores else 0.0,
                "pass_rate": self._pass_rate(all_scores, pass_score) if all_scores else 0.0,
                "successful_count": len(current_knowledge["successful_samples"]),
                "failed_count": len(current_knowledge["failed_samples"]),
                "total_count": len(all_scores),
                "score_distribution": current_knowledge["score_distribution"]
            },
            "successful_examples": current_knowledge["successful_samples"][:3],  # 展示前3个成功案例
            "failed_examples": current_knowledge["failed_samples"][:3],  # 展示前3个失败案例
            "failure_analysis": dict(sorted(
                current_knowledge["common_failure_reasons"].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5])  # 前5个最常见失败原因
        }
        
        # 如果提供了知识库，添加历史洞察
        if knowledge_base:
            feedback_input["historical_insights"] = {
                "best_performing_patterns": knowledge_base.get("successful_patterns", [])[:5],
                "known_pitfalls": knowledge_base.get("failure_patterns", [])[:3],
                "proven_techniques": knowledge_base.get("reusable_snippets", [])[:5]
            }
        
        return feedback_input

    def _select_important_records(self, records: List[Dict], max_records: int, pass_score: float) -> List[Dict]:
        """
        基于重要性选择历史记录，而非简单截断
        
        重要性评分考虑：
        1. 分数变化幅度（突破性改进）
        2. 极端表现（特别高分或特别低分，用于识别模式）
        3. 多样性（避免选择过于相似的记录）
        4. 时间因素（适当偏好最近记录）
        
        Args:
            records: 历史记录列表
            max_records: 最大保留记录数
            pass_score: 及格分数线
            
        Returns:
            按重要性筛选后的记录列表
        """
        if not records or max_records <= 0:
            return []
        
        if len(records) <= max_records:
            return records
        
        scored_records = []
        for i, rec in enumerate(records):
            importance = 0.0
            
            # 1. 分数变化（突破性改进或显著退步）
            if i > 0:
                prev_batches = records[i-1].get("batches", [])
                curr_batches = rec.get("batches", [])
                if prev_batches and curr_batches:
                    prev_score = prev_batches[0].get("avg_score", 0)
                    curr_score = curr_batches[0].get("avg_score", 0)
                    score_change = abs(curr_score - prev_score)
                    importance += score_change * 2.0
            
            # 2. 极端表现（特别好或特别差的记录更重要）
            batches = rec.get("batches", [])
            if batches:
                avg_score = batches[0].get("avg_score", 0)
                if avg_score >= pass_score + 20:  # 特别高分
                    importance += 3.0
                elif avg_score <= max(0, pass_score - 20):  # 特别低分
                    importance += 2.0
            
            # 3. 时间因素（最近的记录权重稍高）
            recency = (i + 1) / len(records)
            importance += recency * 1.0
            
            scored_records.append((importance, i, rec))
        
        # 按重要性排序，取top-k
        scored_records.sort(key=lambda x: x[0], reverse=True)
        selected = [rec for _, _, rec in scored_records[:max_records]]
        
        # 保持时间顺序
        selected.sort(key=lambda x: records.index(x))
        
        return selected

    def _init_knowledge_base_from_insights(self, insights: List[Dict], pass_score: float) -> Dict:
        """
        从历史insights初始化知识库
        
        Args:
            insights: 从MemoryStore获取的历史记录
            pass_score: 及格分数线
            
        Returns:
            初始化的知识库结构
        """
        knowledge_base = {
            "successful_patterns": [],
            "failure_patterns": [],
            "reusable_snippets": []
        }
        
        if not insights:
            return knowledge_base
        
        # 分析历史记录，提取成功和失败模式
        for insight in insights:
            iteration = insight.get("iteration", 0)
            prompt_before = insight.get("prompt_before", "")
            prompt_after = insight.get("prompt_after", "")
            records = insight.get("records", [])
            
            for rec in records:
                avg_score = rec.get("avg_score", 0)
                items = rec.get("items", [])
                
                # 提取成功模式
                if avg_score >= pass_score + 10:
                    pattern = {
                        "prompt_snippet": prompt_before[:200] if len(prompt_before) > 200 else prompt_before,
                        "avg_score": avg_score,
                        "iteration": iteration
                    }
                    knowledge_base["successful_patterns"].append(pattern)
                
                # 提取失败模式
                elif avg_score < pass_score:
                    # 将所有reason转换为字符串，处理可能的字典类型
                    failure_reasons = []
                    for item in items:
                        reason = item.get("reason", "")
                        if isinstance(reason, dict):
                            # 如果是字典，转换为字符串
                            reason = str(reason)
                        elif reason:
                            reason = str(reason)
                        if reason:
                            failure_reasons.append(reason)
                    
                    pattern = {
                        "prompt_snippet": prompt_before[:200] if len(prompt_before) > 200 else prompt_before,
                        "avg_score": avg_score,
                        "common_issues": list(set(failure_reasons))  # 现在可以安全去重
                    }
                    knowledge_base["failure_patterns"].append(pattern)
        
        # 去重并排序
        knowledge_base["successful_patterns"] = sorted(
            knowledge_base["successful_patterns"],
            key=lambda x: x["avg_score"],
            reverse=True
        )[:5]
        
        return knowledge_base

    def _synthesize_from_insights(self, insights: List[Dict], pass_score: float) -> str:
        """
        从历史insights中合成初始建议
        
        Args:
            insights: 历史记录
            pass_score: 及格分数线
            
        Returns:
            合成的建议文本
        """
        if not insights:
            return ""
        
        best_score = 0
        best_prompt = ""
        
        for insight in insights:
            records = insight.get("records", [])
            prompt = insight.get("prompt_after", "")
            
            for rec in records:
                avg_score = rec.get("avg_score", 0)
                if avg_score > best_score:
                    best_score = avg_score
                    best_prompt = prompt
        
        if best_score >= pass_score:
            return f"Historical best performance: {best_score:.1f}. Consider starting from or referencing the successful prompt patterns."
        
        return ""


    def _truncate_text(self, text: str, limit: int) -> str:
        if not isinstance(text, str):
            text = str(text)
        if limit <= 0:
            return text
        if len(text) <= limit:
            return text
        return text[:limit]

    def _summarize_records(self, records: List[Dict], pass_score: float) -> str:
        scores: List[float] = []
        reasons: List[str] = []
        for rec in records or []:
            for it in rec.get("items", []):
                s = it.get("score")
                if s is not None:
                    try:
                        scores.append(float(s))
                    except Exception:
                        pass
                r = it.get("reason")
                if r:
                    reasons.append(str(r))
        avg = self._avg(scores)
        rate = self._pass_rate(scores, pass_score)
        freq: Dict[str, int] = {}
        for r in reasons:
            freq[r] = freq.get(r, 0) + 1
        top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:3]
        top_reasons = ", ".join([t[0] for t in top])
        return f"avg:{avg:.2f};pass_rate:{rate:.2f};top_reasons:{top_reasons}"

    def _summarize_insights(self, insights: List[Dict], pass_score: float) -> str:
        scores: List[float] = []
        reasons: List[str] = []
        for rec in insights or []:
            for batch in rec.get("records", []):
                for it in batch.get("items", []):
                    s = it.get("score")
                    if s is not None:
                        try:
                            scores.append(float(s))
                        except Exception:
                            pass
                    r = it.get("reason")
                    if r:
                        reasons.append(str(r))
        avg = self._avg(scores)
        rate = self._pass_rate(scores, pass_score)
        freq: Dict[str, int] = {}
        for r in reasons:
            freq[r] = freq.get(r, 0) + 1
        top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:3]
        trs = ", ".join([t[0] for t in top])
        return f"prior_avg:{avg:.2f};prior_pass_rate:{rate:.2f};prior_top_reasons:{trs}"

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
