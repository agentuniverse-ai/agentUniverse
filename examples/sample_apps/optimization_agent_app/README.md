# agentUniverse - Optimization Agent Sample Application

## Introduction

This project is a sample application for the agentUniverse framework, demonstrating how to use the optimization work pattern to automatically improve agent prompt performance. Through iterative optimization processes, the system can automatically find higher-quality prompts better suited for specific tasks.

## Core Features

### 1. Intelligent Prompt Optimization
- **Automatic Iterative Improvement**: The system automatically optimizes prompts through multiple rounds of iteration
- **Scoring Feedback Mechanism**: Built-in scoring agents evaluate the quality of each generated result
- **Strategy Learning**: Learns effective prompt construction strategies from the optimization process

### 2. Flexible Optimization Configuration
- **Batch Processing**: Supports batch sample processing to improve optimization efficiency
- **Custom Scoring Standards**: Users can define specialized scoring criteria and pass thresholds
- **Iteration Control**: Configurable maximum iterations, batch size, and other parameters

## Quick Start

### Running Examples

#### Method 1: Run Fund Recommendation Optimization Example
```python
python intelligence/test/optimization_agent.py
```

This example will:
- Use fund product data as optimization samples
- Automatically optimize recommendation copy generation prompts
- Score based on financial compliance, persuasiveness, and other dimensions
- Target an average score of 95+ points

#### Method 2: Run Knowledge Q&A Optimization Example
Modify the `optimization_agent.py` file to use `input_data2`:
```python
result = instance.run(**input_data2)
```

This example will:
- Optimize the quality of explanatory answers
- Ensure answers are accurate and easy to understand
- Target an average score of 90+ points

## Core Components

### 1. Optimization Agent (demo_optimization_agent)
- **Type**: OptimizationAgent
- **Function**: Coordinates the entire optimization process


### 2. Execution Agent (demo_answer_agent)
- **Type**: AnswerAgent
- **Function**: Generates answers based on current prompts

### 3. Scoring Agent (demo_scoring_agent)
- **Type**: ScoringAgent
- **Function**: Quality scores generated answers
- **Criteria**: Evaluates based on user-defined scoring standards

### 4. Feedback Agent (demo_feedback_agent)
- **Type**: FeedbackAgent
- **Function**: Analyzes scoring results and generates optimization suggestions
- **Role**: Guides prompt improvements for the next iteration


## Usage Guide

### Custom Optimization Tasks

1. **Prepare Sample Data**
   ```python
   samples = [
       "Your task sample 1",
       "Your task sample 2", 
       # ... more samples
   ]
   ```

2. **Define Scoring Criteria**
   ```python
   scoring_standard = "Your scoring criteria description"
   ```

3. **Set Optimization Parameters**
   ```python
   input_data = {
       "samples": samples,
       "initial_prompt": "Initial prompt",
       "batch_size": 2,
       "max_iterations": 4,
       "scoring_standard": scoring_standard,
       "avg_score_threshold": 90
   }
   ```

4. **Run Optimization**
   ```python
   result = instance.run(**input_data)
   ```


## Best Practices

### 1. Sample Selection
- Choose representative task samples
- Ensure samples cover main usage scenarios

### 2. Scoring Criteria Design
- Criteria should be specific and quantifiable
- Avoid overly subjective standards
- Consider multi-dimensional evaluation (accuracy, completeness, style, etc.)

## Related Documentation

- [agentUniverse Quick Start Guide](https://github.com/agentuniverse-ai/agentUniverse/blob/master/docs/guidebook/en/Get_Start/Quick_Start.md)
- [agentUniverse Complete Guide](https://github.com/agentuniverse-ai/agentUniverse/blob/master/docs/guidebook/en/Contents.md)

