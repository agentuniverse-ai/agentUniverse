# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03
# @Author  : AgentUniverse Team
# @FileName: test_monitor.py

import unittest
import os
import tempfile
import shutil
import datetime
from unittest.mock import patch, MagicMock

from agentuniverse.base.util.monitor.monitor import Monitor
from agentuniverse.agent.output_object import OutputObject


class MonitorTest(unittest.TestCase):
    """
    Test cases for Monitor class statistics and monitoring features
    """

    def setUp(self) -> None:
        """Set up test fixtures"""
        # Create a temporary directory for monitor data
        self.temp_dir = tempfile.mkdtemp()
        self.monitor = Monitor()
        self.monitor.dir = self.temp_dir
        self.monitor.activate = True

    def tearDown(self) -> None:
        """Clean up test fixtures"""
        # Remove temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_get_llm_statistics_empty(self) -> None:
        """Test get_llm_statistics with no data"""
        stats = self.monitor.get_llm_statistics()
        
        self.assertEqual(stats["total_calls"], 0)
        self.assertEqual(stats["total_tokens"], 0)
        self.assertEqual(stats["avg_cost_time"], 0.0)
        self.assertEqual(len(stats["by_source"]), 0)

    def test_get_agent_statistics_empty(self) -> None:
        """Test get_agent_statistics with no data"""
        stats = self.monitor.get_agent_statistics()
        
        self.assertEqual(stats["total_calls"], 0)
        self.assertEqual(stats["total_tokens"], 0)
        self.assertEqual(stats["avg_cost_time"], 0.0)
        self.assertEqual(len(stats["by_source"]), 0)

    def test_get_llm_statistics_with_data(self) -> None:
        """Test get_llm_statistics with mock data"""
        try:
            import jsonlines
        except ImportError:
            self.skipTest("jsonlines not installed")
        
        # Create mock LLM invocation data
        llm_dir = self.monitor._get_or_create_subdir("llm_invocation")
        filename = f"llm_test_model_{datetime.datetime.now().strftime('%Y-%m-%d-%H')}.jsonl"
        filepath = os.path.join(llm_dir, filename)
        
        records = [
            {
                "source": "test_model",
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "llm_input": {"test": "input"},
                "llm_output": "test output",
                "token_usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "total_tokens": 150
                },
                "cost_time": 1.5
            },
            {
                "source": "test_model",
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "llm_input": {"test": "input2"},
                "llm_output": "test output2",
                "token_usage": {
                    "prompt_tokens": 200,
                    "completion_tokens": 100,
                    "total_tokens": 300
                },
                "cost_time": 2.0
            }
        ]
        
        with jsonlines.open(filepath, 'w') as writer:
            for record in records:
                writer.write(record)
        
        # Test statistics
        stats = self.monitor.get_llm_statistics()
        
        self.assertEqual(stats["total_calls"], 2)
        self.assertEqual(stats["total_tokens"], 450)
        self.assertEqual(stats["total_prompt_tokens"], 300)
        self.assertEqual(stats["total_completion_tokens"], 150)
        self.assertAlmostEqual(stats["avg_cost_time"], 1.75, places=2)
        self.assertIn("test_model", stats["by_source"])

    def test_get_agent_statistics_with_data(self) -> None:
        """Test get_agent_statistics with mock data"""
        try:
            import jsonlines
        except ImportError:
            self.skipTest("jsonlines not installed")
        
        # Create mock Agent invocation data
        agent_dir = self.monitor._get_or_create_subdir("agent_invocation")
        filename = f"agent_test_agent_{datetime.datetime.now().strftime('%Y-%m-%d-%H')}.jsonl"
        filepath = os.path.join(agent_dir, filename)
        
        records = [
            {
                "source": "test_agent",
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "agent_input": {"test": "input"},
                "agent_output": {"test": "output"},
                "token_usage": {
                    "total_tokens": 500
                },
                "cost_time": 3.0
            }
        ]
        
        with jsonlines.open(filepath, 'w') as writer:
            for record in records:
                writer.write(record)
        
        # Test statistics
        stats = self.monitor.get_agent_statistics()
        
        self.assertEqual(stats["total_calls"], 1)
        self.assertEqual(stats["total_tokens"], 500)
        self.assertAlmostEqual(stats["avg_cost_time"], 3.0, places=2)
        self.assertIn("test_agent", stats["by_source"])

    def test_get_llm_statistics_with_date_filter(self) -> None:
        """Test get_llm_statistics with date filtering"""
        try:
            import jsonlines
        except ImportError:
            self.skipTest("jsonlines not installed")
        
        # Create mock data with different dates
        llm_dir = self.monitor._get_or_create_subdir("llm_invocation")
        filename = f"llm_test_model_{datetime.datetime.now().strftime('%Y-%m-%d-%H')}.jsonl"
        filepath = os.path.join(llm_dir, filename)
        
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        
        records = [
            {
                "source": "test_model",
                "date": today.strftime("%Y-%m-%d %H:%M:%S"),
                "llm_input": {"test": "input"},
                "llm_output": "test output",
                "token_usage": {"total_tokens": 100},
                "cost_time": 1.0
            },
            {
                "source": "test_model",
                "date": yesterday.strftime("%Y-%m-%d %H:%M:%S"),
                "llm_input": {"test": "input2"},
                "llm_output": "test output2",
                "token_usage": {"total_tokens": 200},
                "cost_time": 2.0
            }
        ]
        
        with jsonlines.open(filepath, 'w') as writer:
            for record in records:
                writer.write(record)
        
        # Test with date filter (only today)
        start_date = today.strftime("%Y-%m-%d")
        stats = self.monitor.get_llm_statistics(start_date=start_date)
        
        # Should only count today's record
        self.assertEqual(stats["total_calls"], 1)
        self.assertEqual(stats["total_tokens"], 100)

    def test_get_llm_statistics_with_source_filter(self) -> None:
        """Test get_llm_statistics with source filtering"""
        try:
            import jsonlines
        except ImportError:
            self.skipTest("jsonlines not installed")
        
        # Create mock data with different sources
        llm_dir = self.monitor._get_or_create_subdir("llm_invocation")
        now = datetime.datetime.now()
        
        # Create file for model1
        filename1 = f"llm_model1_{now.strftime('%Y-%m-%d-%H')}.jsonl"
        filepath1 = os.path.join(llm_dir, filename1)
        with jsonlines.open(filepath1, 'w') as writer:
            writer.write({
                "source": "model1",
                "date": now.strftime("%Y-%m-%d %H:%M:%S"),
                "llm_input": {},
                "llm_output": "output1",
                "token_usage": {"total_tokens": 100},
                "cost_time": 1.0
            })
        
        # Create file for model2
        filename2 = f"llm_model2_{now.strftime('%Y-%m-%d-%H')}.jsonl"
        filepath2 = os.path.join(llm_dir, filename2)
        with jsonlines.open(filepath2, 'w') as writer:
            writer.write({
                "source": "model2",
                "date": now.strftime("%Y-%m-%d %H:%M:%S"),
                "llm_input": {},
                "llm_output": "output2",
                "token_usage": {"total_tokens": 200},
                "cost_time": 2.0
            })
        
        # Test with source filter
        stats = self.monitor.get_llm_statistics(source="model1")
        
        self.assertEqual(stats["total_calls"], 1)
        self.assertEqual(stats["total_tokens"], 100)
        self.assertIn("model1", stats["by_source"])
        self.assertNotIn("model2", stats["by_source"])

    def test_estimate_cost(self) -> None:
        """Test cost estimation"""
        token_usage = {
            "prompt_tokens": 1000,
            "completion_tokens": 500
        }
        
        cost = self.monitor.estimate_cost(
            token_usage,
            prompt_price_per_1k=0.01,
            completion_price_per_1k=0.03
        )
        
        # Expected: (1000/1000)*0.01 + (500/1000)*0.03 = 0.01 + 0.015 = 0.025
        self.assertAlmostEqual(cost, 0.025, places=4)

    def test_get_daily_summary(self) -> None:
        """Test get_daily_summary"""
        try:
            import jsonlines
        except ImportError:
            self.skipTest("jsonlines not installed")
        
        # Create mock data
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Create LLM data
        llm_dir = self.monitor._get_or_create_subdir("llm_invocation")
        llm_filename = f"llm_test_model_{datetime.datetime.now().strftime('%Y-%m-%d-%H')}.jsonl"
        llm_filepath = os.path.join(llm_dir, llm_filename)
        with jsonlines.open(llm_filepath, 'w') as writer:
            writer.write({
                "source": "test_model",
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "llm_input": {},
                "llm_output": "output",
                "token_usage": {"total_tokens": 100},
                "cost_time": 1.0
            })
        
        # Create Agent data
        agent_dir = self.monitor._get_or_create_subdir("agent_invocation")
        agent_filename = f"agent_test_agent_{datetime.datetime.now().strftime('%Y-%m-%d-%H')}.jsonl"
        agent_filepath = os.path.join(agent_dir, agent_filename)
        with jsonlines.open(agent_filepath, 'w') as writer:
            writer.write({
                "source": "test_agent",
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "agent_input": {},
                "agent_output": {},
                "token_usage": {"total_tokens": 200},
                "cost_time": 2.0
            })
        
        # Test daily summary
        summary = self.monitor.get_daily_summary(today)
        
        self.assertEqual(summary["date"], today)
        self.assertIn("llm", summary)
        self.assertIn("agent", summary)
        self.assertEqual(summary["llm"]["total_calls"], 1)
        self.assertEqual(summary["agent"]["total_calls"], 1)

    def test_trace_agent_invocation_with_token_usage(self) -> None:
        """Test that trace_agent_invocation includes token_usage"""
        try:
            import jsonlines
        except ImportError:
            self.skipTest("jsonlines not installed")
        
        # Mock token usage
        with patch.object(Monitor, 'get_token_usage', return_value={
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }):
            output = OutputObject()
            self.monitor.trace_agent_invocation(
                source="test_agent",
                agent_input={"input": "test"},
                agent_output=output,
                cost_time=1.5
            )
        
        # Verify the record was written
        agent_dir = self.monitor._get_or_create_subdir("agent_invocation")
        files = [f for f in os.listdir(agent_dir) if f.startswith("agent_test_agent")]
        self.assertGreater(len(files), 0)
        
        # Read and verify the record
        filepath = os.path.join(agent_dir, files[0])
        with jsonlines.open(filepath, 'r') as reader:
            records = list(reader)
            if records:
                last_record = records[-1]
                self.assertIn("token_usage", last_record)
                self.assertIn("cost_time", last_record)
                self.assertEqual(last_record["cost_time"], 1.5)


if __name__ == '__main__':
    unittest.main()

