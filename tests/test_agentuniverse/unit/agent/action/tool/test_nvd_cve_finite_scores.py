import json
import math

import pytest

from agentuniverse.agent.action.tool.common_tool.nvd_cve_tool import NvdCveTool


@pytest.mark.parametrize(
    "value",
    [10**400, "1e400", "-Infinity", "NaN", float("inf"), float("nan"), None, True],
)
def test_safe_float_normalizes_non_finite_and_overflow_values(value):
    assert NvdCveTool._safe_float(value) == 0.0


@pytest.mark.parametrize("value", [0, 3, 3.5, "4.25"])
def test_safe_float_preserves_finite_scores(value):
    result = NvdCveTool._safe_float(value)

    assert result == float(value)
    assert math.isfinite(result)


def test_parsed_cvss_is_strictly_json_serializable():
    cvss = NvdCveTool._parse_cvss(
        {
            "cvssMetricV31": [
                {
                    "cvssData": {
                        "baseScore": 10**400,
                        "version": "3.1",
                    },
                    "exploitabilityScore": "1e400",
                    "impactScore": "NaN",
                }
            ]
        }
    )

    assert cvss["base_score"] == 0.0
    assert cvss["exploitability_score"] == 0.0
    assert cvss["impact_score"] == 0.0
    json.dumps(cvss, allow_nan=False)
