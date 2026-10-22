# !/usr/bin/env python3

# @Time    : 2026/10/18
# @Author  : lljjcc426
# @FileName: debate_agent_template.py
from queue import Queue

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.work_pattern.work_pattern_manager import WorkPatternManager
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger


class DebateAgentTemplate(AgentTemplate):
    """Agent template for the debate pattern coordinator.

    This template coordinates proposer, critic and judge agents to reach
    a consensus-driven solution through iterative debate rounds.
    """

    # Sub-agent names
    proposer_agent_name: str = "ProposerAgent"
    critic_agent_name: str = "CriticAgent"
    judge_agent_name: str = "JudgeAgent"

    # Default configuration
    debate_rounds: int = 2
    consensus_threshold: int = 60

    def input_keys(self) -> list[str]:
        """Define input keys required by this agent.

        Returns:
            list[str]: List of input keys
        """
        return ["input"]

    def output_keys(self) -> list[str]:
        """Define output keys produced by this agent.

        Returns:
            list[str]: List of output keys
        """
        return ["output"]

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Parse and prepare input for the debate agent.

        Args:
            input_object (InputObject): The input object containing user data.
            agent_input (dict): The agent input dictionary to be updated.

        Returns:
            dict: Updated agent input dictionary.
        """
        agent_input["input"] = input_object.get_data("input")

        # Get configuration parameters
        agent_input["debate_rounds"] = input_object.get_data("debate_rounds", self.debate_rounds)
        agent_input["consensus_threshold"] = input_object.get_data("consensus_threshold", self.consensus_threshold)

        return agent_input

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        """Execute debate pattern workflow.

        Args:
            input_object (InputObject): The input parameters passed by the user.
            agent_input (dict): The agent input dictionary.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The agent result dictionary.
        """
        # Generate sub-agents
        agents = self._generate_agents()

        # Get debate work pattern instance
        debate_work_pattern = WorkPatternManager().get_instance_obj("debate_work_pattern")

        # Inject agents into work pattern
        debate_work_pattern = debate_work_pattern.set_by_agent_model(**agents)

        # Execute work pattern
        work_pattern_result = self.customized_execute(debate_work_pattern, input_object, agent_input, **kwargs)

        return work_pattern_result

    async def async_execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        """Execute debate pattern workflow asynchronously.

        Args:
            input_object (InputObject): The input parameters passed by the user.
            agent_input (dict): The agent input dictionary.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The agent result dictionary.
        """
        # Generate sub-agents
        agents = self._generate_agents()

        # Get debate work pattern instance
        debate_work_pattern = WorkPatternManager().get_instance_obj("debate_work_pattern")

        # Inject agents into work pattern
        debate_work_pattern = debate_work_pattern.set_by_agent_model(**agents)

        # Execute work pattern asynchronously
        work_pattern_result = await self.async_customized_execute(
            debate_work_pattern, input_object, agent_input, **kwargs
        )

        return work_pattern_result

    def _generate_agents(self) -> dict:
        """Generate proposer, critic and judge agent instances.

        Returns:
            dict: Dictionary containing agent instances.
        """
        agents = {}

        # Get proposer agent
        proposer_agent_name = self.agent_model.profile.get("proposer", self.proposer_agent_name)
        proposer_agent: Agent = AgentManager().get_instance_obj(proposer_agent_name)
        if proposer_agent:
            agents["proposer"] = proposer_agent

        # Get critic agent
        critic_agent_name = self.agent_model.profile.get("critic", self.critic_agent_name)
        critic_agent: Agent = AgentManager().get_instance_obj(critic_agent_name)
        if critic_agent:
            agents["critic"] = critic_agent

        # Get judge agent
        judge_agent_name = self.agent_model.profile.get("judge", self.judge_agent_name)
        judge_agent: Agent = AgentManager().get_instance_obj(judge_agent_name)
        if judge_agent:
            agents["judge"] = judge_agent

        return agents

    def parse_result(self, planner_result: dict) -> dict:
        """Parse the work pattern execution result.

        Args:
            planner_result (dict): Raw result from work pattern execution.

        Returns:
            dict: Parsed result with formatted output.
        """
        final_result = {}

        # Extract result and execution context
        debate_results = planner_result.get("result", [])
        execution_context = planner_result.get("execution_context", {})

        # Build comprehensive output
        output_lines = []
        output_lines.append("=== Debate Pattern Execution Results ===\n")

        # Summary
        output_lines.append(f"Total Rounds: {len(debate_results)}")
        output_lines.append(f"Consensus Reached: {execution_context.get('consensus_reached', False)}")
        output_lines.append(f"Final Score: {execution_context.get('final_score', 0)}\n")

        # Round details
        for idx, debate_round_result in enumerate(debate_results):
            output_lines.append(f"\n--- Round {idx + 1} ---")

            # Proposal result
            proposal_result = debate_round_result.get("proposal_result", {})
            proposal_output = proposal_result.get("output", "")
            output_lines.append(f"Proposal:\n{proposal_output}")

            # Critic result
            critic_result = debate_round_result.get("critic_result", {})
            critic_output = critic_result.get("output", "")
            output_lines.append(f"\nCritique:\n{critic_output}")

            # Judge result
            judge_result = debate_round_result.get("judge_result", {})
            judge_output = judge_result.get("output", {})
            score = judge_result.get("score", 0)
            suggestion = judge_result.get("suggestion", "")

            output_lines.append("\nJudge:")
            output_lines.append(f"  - Score: {score}")
            if suggestion:
                output_lines.append(f"  - Suggestion: {suggestion}")
            if isinstance(judge_output, dict) and judge_output:
                final_answer = judge_output.get("final_answer", "")
                if final_answer:
                    output_lines.append(f"  - Final Answer: {final_answer}")

        # Final result
        if debate_results:
            last_round = debate_results[-1]
            last_judge = last_round.get("judge_result", {})
            last_judge_output = last_judge.get("output", {})
            final_output = last_judge_output.get("final_answer", "") if isinstance(last_judge_output, dict) else ""
            if not final_output:
                last_proposal = last_round.get("proposal_result", {})
                final_output = last_proposal.get("output", "")
            output_lines.append(f"\n\n=== Final Output ===\n{final_output}")
            final_result["output"] = final_output
        else:
            final_result["output"] = ""

        # Store full details
        final_result["full_output"] = "\n".join(output_lines)
        final_result["debate_results"] = debate_results
        final_result["execution_context"] = execution_context

        return final_result

    def customized_execute(self, work_pattern, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        """Execute work pattern with customized logic.

        Args:
            work_pattern: The debate work pattern instance.
            input_object (InputObject): The input parameters.
            agent_input (dict): The agent input dictionary.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The execution result.
        """
        # Add memory to input object if available
        memory: Memory = self.agent_model.memory
        if memory:
            input_object.add_data("memory", memory)

        # Execute work pattern
        work_pattern_result = work_pattern.invoke(input_object=input_object, work_pattern_input=agent_input, **kwargs)

        # Add to memory if available
        if memory:
            self._add_to_memory(memory, agent_input, work_pattern_result)

        # Add stream output
        output_stream: Queue = kwargs.get("output_stream")
        if output_stream:
            parsed_result = self.parse_result(work_pattern_result)
            self.add_output_stream(output_stream, parsed_result.get("full_output", ""))

        return work_pattern_result

    async def async_customized_execute(
        self, work_pattern, input_object: InputObject, agent_input: dict, **kwargs
    ) -> dict:
        """Execute work pattern asynchronously with customized logic.

        Args:
            work_pattern: The debate work pattern instance.
            input_object (InputObject): The input parameters.
            agent_input (dict): The agent input dictionary.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The execution result.
        """
        # Add memory to input object if available
        memory: Memory = self.agent_model.memory
        if memory:
            input_object.add_data("memory", memory)

        # Execute work pattern asynchronously
        work_pattern_result = await work_pattern.async_invoke(
            input_object=input_object, work_pattern_input=agent_input, **kwargs
        )

        # Add to memory if available
        if memory:
            self._add_to_memory(memory, agent_input, work_pattern_result)

        # Add stream output
        output_stream: Queue = kwargs.get("output_stream")
        if output_stream:
            parsed_result = self.parse_result(work_pattern_result)
            self.add_output_stream(output_stream, parsed_result.get("full_output", ""))

        return work_pattern_result

    def _add_to_memory(self, memory: Memory, agent_input: dict, work_pattern_result: dict):
        """Add execution results to memory.

        Args:
            memory (Memory): The memory instance.
            agent_input (dict): The agent input dictionary.
            work_pattern_result (dict): The work pattern execution result.
        """
        # Parse result for storage
        parsed_result = self.parse_result(work_pattern_result)

        # Create message objects for memory
        user_message = {"role": "user", "content": agent_input.get("input", "")}

        assistant_message = {"role": "assistant", "content": parsed_result.get("output", "")}

        # Add to memory
        memory.add_message(user_message)
        memory.add_message(assistant_message)

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> "DebateAgentTemplate":
        """Initialize the debate agent template by component configer.

        Args:
            component_configer (AgentConfiger): The agent configuration object.

        Returns:
            DebateAgentTemplate: Initialized template instance.
        """
        super().initialize_by_component_configer(component_configer)

        # Load configuration
        profile = self.agent_model.profile
        self.proposer_agent_name = profile.get("proposer", self.proposer_agent_name)
        self.critic_agent_name = profile.get("critic", self.critic_agent_name)
        self.judge_agent_name = profile.get("judge", self.judge_agent_name)
        self.debate_rounds = profile.get("debate_rounds", self.debate_rounds)
        self.consensus_threshold = profile.get("consensus_threshold", self.consensus_threshold)

        return self
