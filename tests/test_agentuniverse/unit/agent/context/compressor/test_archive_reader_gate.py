"""Expose the 7Z reader regression suite to the configured smoke target.

The reader tests remain next to the implementation. Importing every TestCase
here keeps the complete suite in the compressor package used as this checkout's
fast repository verification target, rather than relying on a single imported
class that would miss the direct reader tests.
"""

from tests.test_agentuniverse.unit.agent.action.knowledge.reader.file.test_sevenzip_reader import (
    TestSevenZipReaderBasic,
    TestSevenZipReaderComplexScenarios,
    TestSevenZipReaderEdgeCases,
    TestSevenZipReaderPerformance,
    TestSevenZipReaderPreflight,
    TestSevenZipReaderRealWorldScenarios,
    TestSevenZipReaderSizeLimits,
)

__all__ = [
    "TestSevenZipReaderBasic",
    "TestSevenZipReaderComplexScenarios",
    "TestSevenZipReaderEdgeCases",
    "TestSevenZipReaderPerformance",
    "TestSevenZipReaderPreflight",
    "TestSevenZipReaderRealWorldScenarios",
    "TestSevenZipReaderSizeLimits",
]
