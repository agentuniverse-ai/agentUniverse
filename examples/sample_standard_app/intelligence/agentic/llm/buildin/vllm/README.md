# vLLM LLM Configuration Examples

This directory contains example configurations for using vLLM servers with AgentUniverse.

## What is vLLM?

vLLM is a fast and easy-to-use library for LLM inference and serving that provides:

- **High Throughput**: Up to 24x faster than HuggingFace Transformers
- **Memory Efficiency**: PagedAttention reduces memory usage by 50-70%
- **Continuous Batching**: Automatic request batching for improved throughput
- **Quantization Support**: GPTQ, AWQ, SqueezeLLM for reduced memory footprint
- **Multi-GPU Support**: Tensor parallelism for large models
- **OpenAI Compatibility**: Drop-in replacement for OpenAI API

## Prerequisites

### 1. Install vLLM

```bash
pip install vllm
```

### 2. Start vLLM Server

#### Option A: Basic Server (Single Model)

```bash
# Start vLLM server with Llama 3.1 8B
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --port 8000
```

#### Option B: Docker Deployment

```bash
# Pull and run vLLM in Docker
docker run --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -p 8000:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model meta-llama/Llama-3.1-8B-Instruct
```

#### Option C: Multi-GPU for Large Models

```bash
# Run Llama 3.1 70B with tensor parallelism across 4 GPUs
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-70B-Instruct \
    --tensor-parallel-size 4 \
    --port 8000
```

#### Option D: With Quantization (Memory Efficient)

```bash
# Run with AWQ quantization
python -m vllm.entrypoints.openai.api_server \
    --model TheBloke/Llama-2-70B-Chat-AWQ \
    --quantization awq \
    --port 8000
```

### 3. Configure Environment Variables

```bash
# Set vLLM server endpoint
export VLLM_API_BASE="http://localhost:8000/v1"

# Optional: Set API key if you've configured authentication
export VLLM_API_KEY="your-api-key-here"
```

## Configuration Files

### vllm_llama_3_1_8b.yaml
Basic configuration for Llama 3.1 8B model.

**Use case**: General-purpose tasks, development, testing

**Resources**: 1x A100 40GB or 1x RTX 4090

### vllm_llama_3_1_70b.yaml
Advanced configuration with beam search for Llama 3.1 70B model.

**Use case**: High-quality outputs, production deployments

**Resources**: 4x A100 40GB or 2x A100 80GB

**Features**:
- `use_beam_search: true` - Better quality outputs
- `best_of: 3` - Generate 3 sequences, return best
- `length_penalty: 1.2` - Prefer longer responses

### vllm_qwen_2_5_7b.yaml
Configuration for Qwen 2.5 7B model (Chinese + English).

**Use case**: Multilingual applications, Chinese language tasks

**Resources**: 1x A100 40GB or 1x RTX 4090

## Usage Examples

### Python Usage

```python
from agentuniverse.llm.llm_manager import LLMManager

# Load vLLM instance
llm = LLMManager().get_instance_obj("vllm-llama-3.1-8b")

# Simple call
messages = [{"role": "user", "content": "Hello!"}]
response = llm.call(messages)
print(response.text)

# Streaming call
for chunk in llm.call(messages, streaming=True):
    print(chunk.text, end="", flush=True)
```

### Agent Integration

```yaml
# In your agent configuration
agent:
  llm:
    name: 'vllm-llama-3.1-8b'
```

## Performance Tuning

### Server-Side Optimization

```bash
# Tune for your workload
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --max-num-seqs 256 \           # Max concurrent sequences
    --max-num-batched-tokens 8192 \  # Max tokens per batch
    --gpu-memory-utilization 0.9 \   # GPU memory usage (0-1)
    --port 8000
```

### Client-Side Parameters

```yaml
# In your YAML configuration
name: 'vllm-optimized'
model_name: 'meta-llama/Llama-3.1-8B-Instruct'
max_tokens: 2048
temperature: 0.7
# vLLM-specific parameters
use_beam_search: true
best_of: 3
length_penalty: 1.0
```

## Advanced Features

### 1. Quantization for Memory Efficiency

Reduce memory usage by 50-75% with minimal quality loss:

```bash
# GPTQ quantization
python -m vllm.entrypoints.openai.api_server \
    --model TheBloke/Llama-2-70B-Chat-GPTQ \
    --quantization gptq

# AWQ quantization (faster inference)
python -m vllm.entrypoints.openai.api_server \
    --model TheBloke/Llama-2-70B-Chat-AWQ \
    --quantization awq
```

### 2. Long Context Support

```bash
# Enable long context (Llama 3.1 supports up to 128K)
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --max-model-len 131072  # 128K context
```

### 3. Production Stack

For production deployments, use the vLLM Production Stack:

```bash
# Clone production stack
git clone https://github.com/vllm-project/production-stack
cd production-stack

# Configure and deploy
docker-compose up -d
```

Features:
- Load balancing
- Monitoring and metrics
- KV cache offloading
- Multi-model serving

## Troubleshooting

### Connection Issues

```bash
# Test vLLM server is running
curl http://localhost:8000/v1/models

# Check server logs
docker logs <container-id>
```

### Out of Memory

```bash
# Reduce max sequences or batch size
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --max-num-seqs 64 \
    --max-num-batched-tokens 4096

# Or use quantization
python -m vllm.entrypoints.openai.api_server \
    --model TheBloke/Llama-2-13B-Chat-AWQ \
    --quantization awq
```

### Performance Issues

```bash
# Enable continuous batching (default)
# Increase GPU memory utilization
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --gpu-memory-utilization 0.95

# Use tensor parallelism for larger models
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-70B-Instruct \
    --tensor-parallel-size 4
```

## Resources

- **vLLM Documentation**: https://docs.vllm.ai/
- **vLLM GitHub**: https://github.com/vllm-project/vllm
- **Production Stack**: https://github.com/vllm-project/production-stack
- **Model Compatibility**: https://docs.vllm.ai/en/latest/models/supported_models.html

## Cost Comparison

Typical inference costs (relative to cloud APIs):

| Deployment | Cost | Throughput | Setup Complexity |
|-----------|------|------------|------------------|
| Cloud API (OpenAI) | 100% | Baseline | None |
| vLLM Self-hosted | 20-40% | 24x faster | Medium |
| vLLM + Quantization | 10-20% | 20x faster | Medium |
| vLLM Production | 15-30% | 30x faster | High |

**ROI**: vLLM pays for itself after ~1000 requests/day for most workloads.
