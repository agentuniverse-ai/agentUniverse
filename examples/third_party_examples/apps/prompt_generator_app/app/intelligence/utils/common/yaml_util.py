# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/09/16 23:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: yaml_util.py
"""YAML Utility Functions.

Provides YAML file reading, writing, and validation functionality for app.
This utility module focuses on YAML data processing and validation.
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional


class YamlUtil:
    """YAML utility class for file operations and validation."""

    @staticmethod
    def load_yaml_file(file_path: str) -> Dict[str, Any]:
        """Load YAML file.

        Args:
            file_path: Path to the YAML file.

        Returns:
            Parsed YAML content as dictionary.

        Raises:
            FileNotFoundError: If the file does not exist.
            yaml.YAMLError: If YAML format is invalid.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"YAML file not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data if data is not None else {}
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML format in {file_path}: {str(e)}")

    @staticmethod
    def save_yaml_file(data: Dict[str, Any], file_path: str) -> bool:
        """Save data to YAML file.

        Args:
            data: Data to be saved.
            file_path: Target file path.

        Returns:
            True if save was successful.

        Raises:
            IOError: If file writing fails.
        """
        try:
            # Ensure directory exists
            output_dir = os.path.dirname(file_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)

            return True
        except Exception as e:
            raise IOError(f"Failed to save YAML file {file_path}: {str(e)}")

    @staticmethod
    def validate_yaml_structure(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """Validate YAML structure validity.

        Args:
            data: Data to be validated.
            required_fields: List of required fields.

        Returns:
            Validation result with details.
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }

        # Check required fields
        for field in required_fields:
            if field not in data:
                result["errors"].append(f"Missing required field: {field}")
                result["is_valid"] = False

        # Check for empty values
        for field, value in data.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                result["warnings"].append(f"Field '{field}' is empty")

        return result

    @staticmethod
    def merge_yaml_files(file_paths: List[str]) -> Dict[str, Any]:
        """Merge multiple YAML files.

        Args:
            file_paths: List of YAML file paths to merge.

        Returns:
            Merged YAML data.

        Raises:
            FileNotFoundError: If any file does not exist.
            yaml.YAMLError: If any YAML format is invalid.
        """
        merged_data = {}

        for file_path in file_paths:
            data = YamlUtil.load_yaml_file(file_path)
            merged_data.update(data)

        return merged_data

    @staticmethod
    def backup_yaml_file(file_path: str, backup_suffix: str = ".backup") -> str:
        """Create backup of YAML file.

        Args:
            file_path: Path to the YAML file to backup.
            backup_suffix: Suffix for backup file.

        Returns:
            Path to the backup file.

        Raises:
            FileNotFoundError: If source file does not exist.
            IOError: If backup creation fails.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")

        backup_path = file_path + backup_suffix

        try:
            data = YamlUtil.load_yaml_file(file_path)
            YamlUtil.save_yaml_file(data, backup_path)
            return backup_path
        except Exception as e:
            raise IOError(f"Failed to create backup: {str(e)}")

    @staticmethod
    def compare_yaml_files(file_path1: str, file_path2: str) -> Dict[str, Any]:
        """Compare two YAML files.

        Args:
            file_path1: Path to the first YAML file.
            file_path2: Path to the second YAML file.

        Returns:
            Comparison results.
        """
        data1 = YamlUtil.load_yaml_file(file_path1)
        data2 = YamlUtil.load_yaml_file(file_path2)

        differences = []
        all_keys = set(data1.keys()) | set(data2.keys())

        for key in all_keys:
            if key not in data1:
                differences.append(f"Key '{key}' only in file2")
            elif key not in data2:
                differences.append(f"Key '{key}' only in file1")
            elif data1[key] != data2[key]:
                differences.append(f"Key '{key}': '{data1[key]}' != '{data2[key]}'")

        return {
            "are_identical": len(differences) == 0,
            "differences": differences,
            "file1_keys": list(data1.keys()),
            "file2_keys": list(data2.keys())
        }

    @staticmethod
    def extract_metadata(file_path: str) -> Dict[str, Any]:
        """Extract metadata from YAML file.

        Args:
            file_path: Path to the YAML file.

        Returns:
            Extracted metadata information.
        """
        data = YamlUtil.load_yaml_file(file_path)

        file_stat = os.stat(file_path)

        return {
            "file_path": file_path,
            "file_size": file_stat.st_size,
            "modified_time": file_stat.st_mtime,
            "has_metadata": "metadata" in data,
            "metadata": data.get("metadata", {}),
            "key_count": len(data),
            "keys": list(data.keys())
        }
