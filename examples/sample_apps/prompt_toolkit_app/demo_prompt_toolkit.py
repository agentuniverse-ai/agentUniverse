# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 13:45
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: demo_prompt_toolkit.py
"""Demo script for the prompt toolkit functionality."""

import asyncio
from agentuniverse.prompt.prompt_toolkit import (
    PromptToolkit,
    PromptToolkitConfig,
    PromptGenerationRequest
)
from agentuniverse.prompt.prompt_generator import PromptScenario, PromptComplexity
from agentuniverse.prompt.prompt_optimizer import OptimizationStrategy


async def demo_prompt_generation():
    """Demonstrate prompt generation functionality."""
    print("=== Prompt Generation Demo ===")
    
    # Initialize toolkit
    toolkit = PromptToolkit()
    
    # Example 1: Generate a programming assistant prompt
    print("\n1. Generating programming assistant prompt...")
    request1 = PromptGenerationRequest(
        scenario_description="我需要一个编程助手来帮助我写Python代码",
        content="帮助初学者学习Python编程",
        target_audience="初学者",
        domain="技术",
        constraints=["必须使用中文", "提供代码示例"],
        examples=[
            {"input": "如何写一个函数", "output": "def function_name():\n    pass"}
        ],
        tone="友好",
        complexity=PromptComplexity.MEDIUM
    )
    
    result1 = toolkit.generate_prompt_from_request(request1)
    print(f"Generated Prompt:")
    print(f"Introduction: {result1.generated_prompt.introduction}")
    print(f"Target: {result1.generated_prompt.target}")
    print(f"Instruction: {result1.generated_prompt.instruction}")
    print(f"Confidence Score: {result1.confidence_score}")
    print(f"Recommendations: {result1.recommendations}")
    
    # Example 2: Generate a customer service prompt
    print("\n2. Generating customer service prompt...")
    request2 = PromptGenerationRequest(
        scenario_description="我需要一个客服助手来处理客户咨询",
        content="处理产品咨询和投诉",
        target_audience="客户",
        domain="商业",
        constraints=["必须友好", "快速响应"],
        tone="专业友好"
    )
    
    result2 = toolkit.generate_prompt_from_request(request2)
    print(f"Generated Prompt:")
    print(f"Introduction: {result2.generated_prompt.introduction}")
    print(f"Target: {result2.generated_prompt.target}")
    print(f"Instruction: {result2.generated_prompt.instruction}")
    print(f"Confidence Score: {result2.confidence_score}")


async def demo_prompt_optimization():
    """Demonstrate prompt optimization functionality."""
    print("\n=== Prompt Optimization Demo ===")
    
    # Initialize toolkit
    toolkit = PromptToolkit()
    
    # Create a sample prompt to optimize
    from agentuniverse.prompt.prompt_model import AgentPromptModel
    
    sample_prompt = AgentPromptModel(
        introduction="你是一个助手",
        target="帮助用户",
        instruction="请回答问题"
    )
    
    print("Original Prompt:")
    print(f"Introduction: {sample_prompt.introduction}")
    print(f"Target: {sample_prompt.target}")
    print(f"Instruction: {sample_prompt.instruction}")
    
    # Optimize the prompt
    print("\nOptimizing prompt...")
    optimization_result = toolkit.optimize_existing_prompt(
        sample_prompt,
        strategies=[OptimizationStrategy.CLARITY, OptimizationStrategy.STRUCTURE]
    )
    
    print(f"Optimized Prompt:")
    print(f"Original: {optimization_result.original_prompt}")
    print(f"Optimized: {optimization_result.optimized_prompt}")
    print(f"Improvements: {optimization_result.improvements}")
    print(f"Suggestions: {optimization_result.suggestions}")
    print(f"Confidence Score: {optimization_result.confidence_score}")


async def demo_scenario_analysis():
    """Demonstrate scenario analysis functionality."""
    print("\n=== Scenario Analysis Demo ===")
    
    # Initialize toolkit
    toolkit = PromptToolkit()
    
    # Analyze different scenarios
    scenarios = [
        "我需要一个数据分析助手来帮助我分析销售数据",
        "我需要一个创意设计师来帮助我设计logo",
        "我需要一个教育助手来帮助我教学数学",
        "我需要一个研究助手来帮助我写学术论文"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. Analyzing scenario: {scenario}")
        
        # Create request for analysis
        request = PromptGenerationRequest(
            scenario_description=scenario,
            domain="通用"
        )
        
        result = toolkit.generate_prompt_from_request(request)
        
        if result.analysis_result:
            print(f"Recommended Scenario: {result.analysis_result.recommended_scenario.value}")
            print(f"Complexity Level: {result.analysis_result.complexity_level.value}")
            print(f"Confidence Score: {result.analysis_result.confidence_score}")
            print(f"Suggestions: {result.analysis_result.suggestions}")


async def demo_batch_generation():
    """Demonstrate batch prompt generation."""
    print("\n=== Batch Generation Demo ===")
    
    # Initialize toolkit
    toolkit = PromptToolkit()
    
    # Create multiple requests
    requests = [
        PromptGenerationRequest(
            scenario_description="编程助手",
            domain="技术",
            target_audience="开发者"
        ),
        PromptGenerationRequest(
            scenario_description="客服助手",
            domain="商业",
            target_audience="客户"
        ),
        PromptGenerationRequest(
            scenario_description="教育助手",
            domain="教育",
            target_audience="学生"
        )
    ]
    
    print("Generating multiple prompts in batch...")
    results = toolkit.batch_generate_prompts(requests)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Generated Prompt:")
        print(f"Introduction: {result.generated_prompt.introduction}")
        print(f"Target: {result.generated_prompt.target}")
        print(f"Confidence Score: {result.confidence_score}")


async def demo_quality_analysis():
    """Demonstrate prompt quality analysis."""
    print("\n=== Quality Analysis Demo ===")
    
    # Initialize toolkit
    toolkit = PromptToolkit()
    
    # Create a sample prompt
    from agentuniverse.prompt.prompt_model import AgentPromptModel
    
    sample_prompt = AgentPromptModel(
        introduction="你是一个专业的AI助手",
        target="你的目标是帮助用户解决各种问题",
        instruction="请按照以下步骤回答问题：1. 理解问题 2. 分析问题 3. 提供解决方案"
    )
    
    print("Analyzing prompt quality...")
    quality_analysis = toolkit.analyze_prompt_quality(sample_prompt)
    
    print(f"Overall Score: {quality_analysis['overall_score']}")
    print("Quality Scores:")
    for score in quality_analysis['quality_scores']:
        print(f"  {score['metric']}: {score['score']} - {score['feedback']}")
    
    print("Recommendations:")
    for recommendation in quality_analysis['recommendations']:
        print(f"  - {recommendation}")


async def demo_export_functionality():
    """Demonstrate export functionality."""
    print("\n=== Export Functionality Demo ===")
    
    # Initialize toolkit
    toolkit = PromptToolkit()
    
    # Create a sample prompt
    from agentuniverse.prompt.prompt_model import AgentPromptModel
    
    sample_prompt = AgentPromptModel(
        introduction="你是一个专业的AI助手",
        target="你的目标是帮助用户解决各种问题",
        instruction="请按照以下步骤回答问题：1. 理解问题 2. 分析问题 3. 提供解决方案"
    )
    
    # Export as YAML
    print("Exporting as YAML...")
    yaml_config = toolkit.export_prompt_config(sample_prompt, "yaml")
    print("YAML Configuration:")
    print(yaml_config)
    
    # Export as JSON
    print("\nExporting as JSON...")
    json_config = toolkit.export_prompt_config(sample_prompt, "json")
    print("JSON Configuration:")
    print(json_config)


async def main():
    """Main demo function."""
    print("Prompt Toolkit Demo")
    print("=" * 50)
    
    try:
        # Run all demos
        await demo_prompt_generation()
        await demo_prompt_optimization()
        await demo_scenario_analysis()
        await demo_batch_generation()
        await demo_quality_analysis()
        await demo_export_functionality()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
