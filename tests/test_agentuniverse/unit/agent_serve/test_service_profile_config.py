from pathlib import Path


SOURCE = Path(
    "agentuniverse/agent_serve/service.py"
).read_text(encoding="utf-8")


def test_service_run_normalizes_missing_profile_mapping():
    assert "if not isinstance(profile, dict):" in SOURCE
    assert "if not isinstance(llm_model, dict):" in SOURCE
    assert "self.agent.agent_model.profile = profile" in SOURCE
