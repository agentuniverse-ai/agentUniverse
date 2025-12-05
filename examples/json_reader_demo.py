#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
JsonReader Demo - Demonstrates how to use JsonReader to load JSON files as knowledge.

This example shows:
1. Basic JSON object loading
2. JSON array loading
3. Loading with custom metadata
4. Integration with knowledge base
"""

import json
import tempfile
from pathlib import Path

from agentuniverse.agent.action.knowledge.reader.file.json_reader import JsonReader


def demo_basic_usage():
    """Basic usage of JsonReader"""
    print("=" * 60)
    print("Demo 1: Basic JSON Object Loading")
    print("=" * 60)

    # Create a sample JSON file
    sample_data = {
        "project": "agentUniverse",
        "version": "0.0.19",
        "features": ["knowledge", "reader", "json"],
        "config": {
            "enabled": True,
            "max_size": 1024
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
        temp_path = f.name

    try:
        # Load JSON file using JsonReader
        reader = JsonReader()
        documents = reader.load_data(temp_path)

        print(f"Loaded {len(documents)} document(s)")
        print(f"\nDocument text (first 200 chars):")
        print(documents[0].text[:200] + "...")
        print(f"\nDocument metadata:")
        for key, value in documents[0].metadata.items():
            print(f"  {key}: {value}")

    finally:
        Path(temp_path).unlink()


def demo_array_loading():
    """Loading JSON array"""
    print("\n" + "=" * 60)
    print("Demo 2: JSON Array Loading")
    print("=" * 60)

    users = [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "user"},
        {"id": 3, "name": "Charlie", "role": "user"}
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
        temp_path = f.name

    try:
        reader = JsonReader()
        documents = reader.load_data(temp_path)

        print(f"Loaded {len(documents)} document(s)")
        print(f"JSON type: {documents[0].metadata['json_type']}")
        print(f"\nContent preview:")
        print(documents[0].text[:150] + "...")

    finally:
        Path(temp_path).unlink()


def demo_with_metadata():
    """Loading with custom metadata"""
    print("\n" + "=" * 60)
    print("Demo 3: Loading with Custom Metadata")
    print("=" * 60)

    config_data = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "agentuniverse_db"
        },
        "cache": {
            "enabled": True,
            "ttl": 3600
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)
        temp_path = f.name

    try:
        reader = JsonReader()
        # Add custom metadata
        ext_info = {
            "source": "config_loader",
            "environment": "development",
            "priority": "high"
        }
        documents = reader.load_data(temp_path, ext_info=ext_info)

        print(f"Document metadata:")
        for key, value in documents[0].metadata.items():
            print(f"  {key}: {value}")

    finally:
        Path(temp_path).unlink()


def demo_unicode_support():
    """Demonstrating Unicode support"""
    print("\n" + "=" * 60)
    print("Demo 4: Unicode Support (中文支持)")
    print("=" * 60)

    multilingual_data = {
        "title": "多语言知识库",
        "description": "agentUniverse supports multiple languages",
        "languages": ["English", "中文", "日本語", "한국어"],
        "emoji": "🚀 🎉 ✨",
        "content": {
            "en": "Knowledge base system",
            "zh": "知识库系统",
            "ja": "知識ベースシステム"
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(multilingual_data, f, ensure_ascii=False, indent=2)
        temp_path = f.name

    try:
        reader = JsonReader()
        documents = reader.load_data(temp_path)

        print("Unicode characters are properly preserved:")
        print(documents[0].text[:300])

    finally:
        Path(temp_path).unlink()


def demo_error_handling():
    """Demonstrating error handling"""
    print("\n" + "=" * 60)
    print("Demo 5: Error Handling")
    print("=" * 60)

    reader = JsonReader()

    # Test 1: Invalid JSON
    print("\n1. Testing invalid JSON handling:")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        f.write('{"invalid": json syntax}')
        temp_path = f.name

    try:
        reader.load_data(temp_path)
        print("  ❌ Should have raised JSONDecodeError")
    except json.JSONDecodeError as e:
        print(f"  ✓ Correctly caught JSONDecodeError")
    finally:
        Path(temp_path).unlink()

    # Test 2: Non-existent file
    print("\n2. Testing non-existent file handling:")
    try:
        reader.load_data("/tmp/nonexistent_file_12345.json")
        print("  ❌ Should have raised FileNotFoundError")
    except FileNotFoundError:
        print(f"  ✓ Correctly caught FileNotFoundError")


if __name__ == "__main__":
    print("\n" + "🚀 " * 20)
    print("JsonReader Demonstration")
    print("🚀 " * 20 + "\n")

    demo_basic_usage()
    demo_array_loading()
    demo_with_metadata()
    demo_unicode_support()
    demo_error_handling()

    print("\n" + "=" * 60)
    print("All demos completed successfully! ✨")
    print("=" * 60 + "\n")
