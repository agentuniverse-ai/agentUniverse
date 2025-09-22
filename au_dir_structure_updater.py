# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/17 20:54
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: au_dir_structure_updater.py
import os
import shutil
from pathlib import Path

from ruamel.yaml import YAML


def create_directory_structure(base_path):
    """Create new directory structure"""
    directories = [
        'boostrap/intelligence',
        'boostrap/platform',
        'intelligence/agentic/agent/agent_instance',
        'intelligence/agentic/agent/agent_template',
        'intelligence/agentic/knowledge/store',
        'intelligence/agentic/knowledge/rag_router',
        'intelligence/agentic/knowledge/doc_processor',
        'intelligence/agentic/knowledge/query_paraphraser',
        'intelligence/agentic/knowledge/raw_knowledge_file',
        'intelligence/agentic/llm',
        'intelligence/agentic/prompt',
        'intelligence/agentic/memory',
        'intelligence/agentic/memory/memory_compressor',
        'intelligence/agentic/memory/memory_storage',
        'intelligence/agentic/tool',
        'intelligence/agentic/planner',
        'intelligence/agentic/work_pattern',
        'intelligence/service',
        'intelligence/service/agent_service',
        'intelligence/service/classic_service',
        'intelligence/dal',
        'intelligence/integration',
        'intelligence/utils',
        'intelligence/test',
        'platform/difizen/product/agent',
        'platform/difizen/product/knowledge',
        'platform/difizen/product/tool',
        'platform/difizen/product/plugin',
        'platform/difizen/product/planner',
        'platform/difizen/product/llm',
        'platform/difizen/resources',
        'platform/difizen/workflow',
    ]

    for directory in directories:
        Path(os.path.join(base_path, directory)).mkdir(parents=True, exist_ok=True)


def update_yaml_file(file_path, migration_rules):
    """Update metadata module info in the YAML file"""
    yaml = YAML()
    with open(file_path, 'r', encoding='utf-8') as file:
        content = yaml.load(file)

    update_yaml_flag = False
    if 'metadata' in content and 'module' in content['metadata']:
        original_module = content['metadata']['module']
        for rule in migration_rules:
            if rule['source'].replace('/', '.') in original_module:
                new_module = original_module.replace(
                    rule['source'].replace('/', '.'),
                    rule['target'].replace('/', '.')
                )
                content['metadata']['module'] = new_module
                update_yaml_flag = True
                break
    if update_yaml_flag:
        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.dump(content, file)


def update_python_file(file_path, migration_rules):
    """Update import paths in the Python files"""
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(file_path, 'w', encoding='utf-8') as file:
        for line in lines:
            for rule in migration_rules:
                source_module = rule['source'].replace('/', '.')
                target_module = rule['target'].replace('/', '.')

                if line.startswith('from ') or line.startswith('import '):
                    if source_module in line:
                        line = line.replace(source_module, target_module)
            file.write(line)


def migrate_files(source_root, target_root):
    """Migrate files from source to target directory."""
    migration_rules = [
        {
            'source': 'app/core/agent',
            'target': 'intelligence/agentic/agent/agent_instance'
        },
        {
            'source': 'app/core/knowledge',
            'target': 'intelligence/agentic/knowledge'
        },
        {
            'source': 'app/util',
            'target': 'intelligence/utils'
        },
        {
            'source': 'app/examples',
            'target': 'intelligence/test'
        },
        {
            'source': 'app/resources',
            'target': 'platform/difizen/resources'
        },
        {
            'source': 'app/core/llm',
            'target': 'intelligence/agentic/llm'
        },
        {
            'source': 'app/core/prompt',
            'target': 'intelligence/agentic/prompt'
        },
        {
            'source': 'app/core/memory',
            'target': 'intelligence/agentic/memory'
        },
        {
            'source': 'app/core/store',
            'target': 'intelligence/agentic/knowledge/store'
        },
        {
            'source': 'app/core/doc_processor',
            'target': 'intelligence/agentic/knowledge/doc_processor'
        },
        {
            'source': 'app/core/query_paraphraser',
            'target': 'intelligence/agentic/knowledge/query_paraphraser'
        },
        {
            'source': 'app/core/rag_router',
            'target': 'intelligence/agentic/knowledge/rag_router'
        },
        {
            'source': 'app/core/workflow',
            'target': 'platform/difizen/workflow'
        },
        {
            'source': 'app/core/planner',
            'target': 'intelligence/agentic/planner'
        },
        {
            'source': 'app/core/tool',
            'target': 'intelligence/agentic/tool'
        },
        {
            'source': 'app/core/service',
            'target': 'intelligence/service/agent_service'
        },
        {
            'source': 'app/core/product/agent',
            'target': 'platform/difizen/product/agent'
        },
        {
            'source': 'app/core/product/knowledge',
            'target': 'platform/difizen/product/knowledge'
        },
        {
            'source': 'app/core/product/planner',
            'target': 'platform/difizen/product/planner'
        },
        {
            'source': 'app/core/product/llm',
            'target': 'platform/difizen/product/llm'
        },
        {
            'source': 'app/core/product/plugin',
            'target': 'platform/difizen/product/plugin'
        },
        {
            'source': 'app/core/product/tool',
            'target': 'platform/difizen/product/tool'
        },
        {
            'source': 'app/test',
            'target': 'intelligence/test'
        },
        {
            'source': 'app/bootstrap/product_application.py',
            'target': 'bootstrap/platform'
        },
        {
            'source': 'app/bootstrap/product_application.py',
            'target': 'bootstrap/platform'
        },
        {
            'source': 'app/bootstrap/server_application.py',
            'target': 'boostrap/intelligence'
        },
        {
            'source': 'app/bootstrap/server_application.py',
            'target': 'boostrap/intelligence'
        },
    ]

    for rule in migration_rules:
        source_path = os.path.join(source_root, rule['source'])
        target_path = os.path.join(target_root, rule['target'])

        if os.path.exists(source_path):
            print(f"Migrating from {source_path} to {target_path}")

            if os.path.isfile(source_path):
                # If the source path is a file, then move it directly.
                os.makedirs(target_path, exist_ok=True)
                shutil.move(source_path, os.path.join(target_path, os.path.basename(source_path)))
                print(f"Moving {source_path} to {target_path}")
                if source_path.endswith('.yaml'):
                    update_yaml_file(os.path.join(target_path, os.path.basename(source_path)), migration_rules)
                elif source_path.endswith('.py'):
                    update_python_file(os.path.join(target_path, os.path.basename(source_path)), migration_rules)
            else:
                # Retrieve all files from the source directory.
                for root, _, files in os.walk(source_path):
                    for file in files:
                        source_file = os.path.join(root, file)
                        relative_path = os.path.relpath(root, source_path)
                        target_dir = os.path.join(target_path, relative_path)

                        os.makedirs(target_dir, exist_ok=True)

                        # Move file
                        target_file = os.path.join(target_dir, file)
                        shutil.move(source_file, target_file)
                        print(f"Moving {source_file} to {target_file}")

                        if source_file.endswith('.yaml'):
                            update_yaml_file(target_file, migration_rules)
                        elif source_file.endswith('.py'):
                            update_python_file(target_file, migration_rules)


def main():
    # Get the current working directory.
    current_dir = os.getcwd()

    # Create a new directory structure.
    create_directory_structure(current_dir)

    # Perform file migration.
    migrate_files(current_dir, current_dir)

    print("Migration completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
