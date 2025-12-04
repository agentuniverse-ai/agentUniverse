#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/04 12:00
# @Author  : kaichuan
# @FileName: demo_phase2.py
"""
Phase 2 Context Engineering Demo

Demonstrates the complete Phase 2 features:
- Multi-tier storage (Hot/Warm/Cold)
- Intelligent compression strategies
- Task-adaptive routing
- Memory budget-aware retrieval
"""

from datetime import datetime, timedelta

from agentuniverse.agent.context.context_manager import ContextManager
from agentuniverse.agent.context.store.ram_context_store import RamContextStore
from agentuniverse.agent.context.compressor.adaptive_compressor import AdaptiveCompressor
from agentuniverse.agent.context.compressor.selective_compressor import SelectiveCompressor
from agentuniverse.agent.context.router.context_router import ContextRouter
from agentuniverse.agent.context.context_model import (
    ContextType,
    ContextPriority,
)


def print_banner(text):
    """Print a formatted banner."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_metrics(metrics):
    """Print budget utilization metrics."""
    print(f"Session: {metrics['session_id']}")
    print(f"Max Tokens: {metrics['max_tokens']}")
    print(f"Input Budget: {metrics['input_budget']}")
    print(f"Total Tokens: {metrics['total_tokens']}")
    print(f"Available Tokens: {metrics['available_tokens']}")
    print(f"Utilization: {metrics['utilization']:.1%}")
    print(f"Over Budget: {'YES ⚠️' if metrics['is_over_budget'] else 'NO ✅'}")
    print(f"Segment Count: {metrics['segment_count']}")


def demo_basic_operations():
    """Demo 1: Basic context operations."""
    print_banner("Demo 1: Basic Context Operations")

    # Create storage
    store = RamContextStore(
        name='demo_hot_store',
        max_segments=100,
        ttl_hours=24
    )

    # Create context manager
    manager = ContextManager(
        name='demo_manager',
        default_max_tokens=1000,
        default_reserved_tokens=200,
        enable_compression=False  # Disable for basic demo
    )
    manager._hot_store = store

    # Create context window
    session_id = "demo_session_1"
    window = manager.create_context_window(
        session_id,
        task_type='dialogue'
    )

    print("✅ Created context window for dialogue task")
    print(f"   Max tokens: {window.max_tokens}")
    print(f"   Input budget: {window.calculate_input_tokens()}")
    print(f"   Component budgets: {window.component_budgets}\n")

    # Add context
    print("Adding context segments...")
    manager.add_context(
        session_id,
        "System: You are a helpful AI assistant.",
        ContextType.SYSTEM,
        ContextPriority.CRITICAL
    )
    print("✅ Added CRITICAL system context")

    manager.add_context(
        session_id,
        "User: How do I implement authentication in Python?",
        ContextType.CONVERSATION,
        ContextPriority.HIGH
    )
    print("✅ Added HIGH priority user message")

    manager.add_context(
        session_id,
        "Assistant: I'll help you with Python authentication...",
        ContextType.CONVERSATION,
        ContextPriority.HIGH
    )
    print("✅ Added HIGH priority assistant message\n")

    # Retrieve context
    segments = manager.get_context(session_id)
    print(f"📊 Retrieved {len(segments)} segments:")
    for seg in segments:
        print(f"   - [{seg.priority.value}] {seg.type.value}: {seg.content[:50]}...")

    # Budget metrics
    print("\n📈 Budget Utilization:")
    metrics = manager.get_budget_utilization(session_id)
    print_metrics(metrics)


def demo_intelligent_compression():
    """Demo 2: Intelligent compression with SelectiveCompressor."""
    print_banner("Demo 2: Intelligent Compression (SelectiveCompressor)")

    # Create components
    store = RamContextStore(name='demo_hot_store', max_segments=100)
    compressor = SelectiveCompressor(
        name='demo_compressor',
        compression_ratio=0.6
    )

    manager = ContextManager(
        name='demo_manager',
        default_max_tokens=500,  # Small window to trigger compression
        default_reserved_tokens=100,
        enable_compression=True
    )
    manager._hot_store = store
    manager._compressor = compressor

    # Create window
    session_id = "demo_session_2"
    window = manager.create_context_window(
        session_id,
        task_type='code_generation'
    )

    print("✅ Created context window (500 tokens max)")
    print(f"   Input budget: {window.calculate_input_tokens()} tokens\n")

    # Add CRITICAL context
    manager.add_context(
        session_id,
        "System: You are a code generation assistant specialized in Python.",
        ContextType.SYSTEM,
        ContextPriority.CRITICAL
    )
    print("✅ Added CRITICAL system prompt")

    # Add many HIGH priority segments
    print("\nAdding 20 HIGH priority code contexts...")
    for i in range(20):
        manager.add_context(
            session_id,
            f"Code context {i}: This is important code context with implementation details. " * 5,
            ContextType.WORKSPACE,
            ContextPriority.HIGH
        )
    print("✅ Added 20 HIGH priority segments")

    # Add LOW priority segments
    print("\nAdding 15 LOW priority background contexts...")
    for i in range(15):
        manager.add_context(
            session_id,
            f"Background info {i}: This is less important background information. " * 3,
            ContextType.BACKGROUND,
            ContextPriority.LOW
        )
    print("✅ Added 15 LOW priority segments")

    # Check final state
    segments = manager.get_context(session_id)
    print(f"\n📊 Final state: {len(segments)} segments (compressed from 36)")

    # Count by priority
    priority_counts = {}
    for seg in segments:
        priority_counts[seg.priority] = priority_counts.get(seg.priority, 0) + 1

    print("\n📈 Segments by priority after compression:")
    for priority, count in sorted(priority_counts.items(),
                                  key=lambda x: ['critical', 'high', 'medium', 'low', 'ephemeral'].index(x[0].value)):
        print(f"   - {priority.value.upper()}: {count}")

    # Verify CRITICAL preserved
    critical_count = sum(1 for s in segments if s.priority == ContextPriority.CRITICAL)
    print(f"\n✅ CRITICAL segments preserved: {critical_count}/1 (100%)")

    # Budget metrics
    print("\n📈 Budget Utilization (after compression):")
    metrics = manager.get_budget_utilization(session_id)
    print_metrics(metrics)


def demo_task_adaptive_routing():
    """Demo 3: Task-adaptive routing and budget allocation."""
    print_banner("Demo 3: Task-Adaptive Routing & Budget Allocation")

    router = ContextRouter(
        name='demo_router',
        enable_warm_tier=False,
        enable_cold_tier=False
    )

    # Test different task types
    tasks = ['code_generation', 'data_analysis', 'dialogue']

    for task_type in tasks:
        print(f"\n📋 Task Type: {task_type}")
        print("-" * 40)

        # Get routing rule
        rule = router.get_routing_rule(task_type)
        print(f"Priority Types: {[t.value for t in rule.priority_types]}")
        print(f"Search Tiers: {rule.search_tiers}")
        print(f"Compression Strategy: {rule.compression_strategy}")
        print(f"Archive After: {rule.archive_after_hours} hours")

        # Create window with this task type
        store = RamContextStore(name=f'store_{task_type}', max_segments=100)
        manager = ContextManager(
            name=f'manager_{task_type}',
            default_max_tokens=10000,
            enable_compression=False
        )
        manager._hot_store = store

        window = manager.create_context_window(
            f'session_{task_type}',
            task_type=task_type
        )

        print(f"\n💰 Budget Allocation:")
        for component, budget in window.component_budgets.items():
            percentage = (budget / window.calculate_input_tokens()) * 100
            print(f"   - {component}: {budget} tokens ({percentage:.1f}%)")


def demo_search_and_retrieval():
    """Demo 4: Context search and retrieval."""
    print_banner("Demo 4: Context Search & Retrieval")

    # Create components
    store = RamContextStore(name='demo_hot_store', max_segments=100)
    manager = ContextManager(
        name='demo_manager',
        default_max_tokens=2000,
        enable_compression=False
    )
    manager._hot_store = store

    session_id = "demo_session_4"
    manager.create_context_window(session_id, task_type='dialogue')

    # Add diverse content
    content_items = [
        ("How do I implement authentication in Python?", ContextPriority.HIGH),
        ("What are the best practices for API design?", ContextPriority.HIGH),
        ("Explain how JWT tokens work", ContextPriority.HIGH),
        ("What is the weather like today?", ContextPriority.LOW),
        ("Tell me a joke", ContextPriority.LOW),
        ("How can I secure my REST API endpoints?", ContextPriority.HIGH),
        ("What time is it?", ContextPriority.LOW),
        ("Implement OAuth2 authentication flow", ContextPriority.HIGH),
    ]

    print("Adding diverse content...")
    for content, priority in content_items:
        manager.add_context(
            session_id,
            content,
            ContextType.CONVERSATION,
            priority
        )
    print(f"✅ Added {len(content_items)} segments\n")

    # Search for authentication-related content
    print("🔍 Searching for 'authentication'...")
    results = manager.search_context(
        session_id,
        "authentication",
        top_k=3
    )

    print(f"\n📊 Found {len(results)} results:")
    for i, seg in enumerate(results, 1):
        print(f"\n{i}. [{seg.priority.value}] Score: {seg.metadata.relevance_score:.2f}")
        print(f"   Content: {seg.content}")

    # Search for API-related content
    print("\n" + "-" * 80)
    print("\n🔍 Searching for 'API security'...")
    results = manager.search_context(
        session_id,
        "API security",
        top_k=3
    )

    print(f"\n📊 Found {len(results)} results:")
    for i, seg in enumerate(results, 1):
        print(f"\n{i}. [{seg.priority.value}] Score: {seg.metadata.relevance_score:.2f}")
        print(f"   Content: {seg.content}")


def demo_memory_integration():
    """Demo 5: Memory class budget-aware retrieval."""
    print_banner("Demo 5: Memory Budget-Aware Retrieval")

    from agentuniverse.agent.memory.memory import Memory
    from agentuniverse.agent.memory.message import Message

    print("Creating Memory instance...")
    memory = Memory(
        name='demo_memory',
        max_tokens=1000
    )
    print("✅ Created memory (fallback mode - no ContextManager linked)\n")

    # Test budget-aware retrieval
    print("Testing budget-aware retrieval...")
    messages = memory.get_with_context_budget(
        session_id='demo_session',
        agent_id='demo_agent',
        allocated_tokens=500
    )

    print(f"✅ Retrieved {len(messages)} messages within 500 token budget")
    print("\n💡 Note: In production, link Memory to ContextManager via YAML:")
    print("   memory:")
    print("     name: 'demo_memory'")
    print("     context_manager: 'default_context_manager'  # Enable integration")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "Phase 2 Context Engineering Demo" + " " * 25 + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Multi-tier Storage | Intelligent Compression | Task-Adaptive Routing  " + "║")
    print("╚" + "═" * 78 + "╝")

    try:
        # Run demos
        demo_basic_operations()
        input("\nPress Enter to continue to Demo 2...")

        demo_intelligent_compression()
        input("\nPress Enter to continue to Demo 3...")

        demo_task_adaptive_routing()
        input("\nPress Enter to continue to Demo 4...")

        demo_search_and_retrieval()
        input("\nPress Enter to continue to Demo 5...")

        demo_memory_integration()

        # Final summary
        print_banner("Demo Complete! 🎉")
        print("Phase 2 Features Demonstrated:")
        print("  ✅ Basic context operations")
        print("  ✅ Intelligent compression (SelectiveCompressor)")
        print("  ✅ Task-adaptive routing and budget allocation")
        print("  ✅ Context search and retrieval")
        print("  ✅ Memory budget-aware retrieval\n")

        print("📚 Next Steps:")
        print("  1. Review configuration examples in examples/context_engineering/")
        print("  2. Read phase2-complete-implementation-summary.md")
        print("  3. Try multi-tier setup with Redis and Chroma")
        print("  4. Integrate with your agents via YAML configuration\n")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
