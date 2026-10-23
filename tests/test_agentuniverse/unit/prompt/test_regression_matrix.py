"""Golden matrix tests exercise actual PromptManager/Agent/ChatPrompt assembly."""

import copy
import json
import socket
import subprocess
import sys
from unittest.mock import patch

import pytest

from agentuniverse.base.config.component_configer.configers.prompt_configer import PromptConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.regression_matrix import compare_baseline, render_matrix


@pytest.fixture
def registered():
    manager = PromptManager()
    previous = manager._instance_obj_map.copy()
    config = Configer("prompt/test/v1.yaml")
    config.value = {
        "introduction": "You help {name}.",
        "target": "目标",
        "instruction": "Answer {question}.",
        "metadata": {"version": "matrix.v1", "type": "PROMPT"},
    }
    prompt = Prompt().initialize_by_component_configer(PromptConfiger().load_by_configer(config))
    manager.register("matrix.v1", prompt)
    try:
        yield prompt
    finally:
        manager._instance_obj_map.clear()
        manager._instance_obj_map.update(previous)


def case(**kwargs):
    return {
        "id": "english",
        "profile": {"prompt_version": "matrix.v1"},
        "inputs": {},
        "bindings": {"name": "Ada", "question": "why"},
        **kwargs,
    }


def test_real_inheritance_and_rendered_messages(registered):
    report = render_matrix([case()])
    assert report["cases"] == [
        {
            "id": "english",
            "status": "rendered",
            "messages": [
                {"role": "system", "content": "You help Ada.\n目标"},
                {"role": "human", "content": "Answer why."},
            ],
        }
    ]
    report = render_matrix([case(profile={"prompt_version": "matrix.v1", "instruction": "自定义 {question}"})])
    assert report["cases"][0]["messages"][-1]["content"] == "自定义 why"


def test_missing_variables_and_prompt_are_explicit(registered):
    report = render_matrix([case(bindings={})])
    assert report["cases"][0]["missing"] == ["name", "question"]
    assert report["cases"][0]["status"] == "missing_variables"
    missing = render_matrix([case(profile={"prompt_version": "absent"})])
    assert missing["cases"][0]["status"] == "missing_prompt"
    assert not compare_baseline(report, report)["matches"]


def test_multimodal_binding_no_network_or_llm(registered):
    from agentuniverse.llm.llm import LLM

    inputs = {
        "image_urls": ["https://example.invalid/a.png", {"url": "https://example.invalid/b.png", "detail": "low"}],
        "audio_url": "https://example.invalid/a.wav",
    }
    with (
        patch.object(socket, "socket", side_effect=AssertionError("network")),
        patch.object(LLM, "call", side_effect=AssertionError("LLM")),
    ):
        result = render_matrix([case(inputs=inputs)])
    row = result["cases"][0]
    assert row["status"] == "rendered"
    assert len(row["messages"]) == 5
    assert row["messages"][3]["content"][0]["image_url"]["detail"] == "low"
    assert row["messages"][4]["content"][0]["input_audio"]["data"] == inputs["audio_url"]


def test_error_does_not_echo_fixture_content():
    report = render_matrix([case(profile={"instruction": "secret {bad"})])
    assert report["cases"][0]["status"] == "render_error"
    assert "secret" not in json.dumps(report)


def test_golden_diff_and_no_mutation(registered):
    fixture = case()
    prior_case, prior_prompt = copy.deepcopy(fixture), copy.deepcopy(registered.model_dump())
    baseline = render_matrix([fixture])
    fixture["bindings"]["question"] = "何故"
    current = render_matrix([fixture])
    result = compare_baseline(current, baseline)
    assert not result["matches"]
    assert "-      " in result["diff"] and "何故" in result["diff"]
    assert baseline == render_matrix([prior_case])
    assert registered.model_dump() == prior_prompt
    assert render_matrix([case(id="z"), case(id="a")]) == render_matrix([case(id="a"), case(id="z")])


@pytest.mark.parametrize(
    "bad",
    [
        case(id=""),
        case(inputs={"image_urls": ["/private/a.png"]}),
        case(inputs={"audio_url": "file:///private.wav"}),
        case(profile={"llm_model": {"name": "paid"}}),
        case(inputs={"image_urls": "https://example.invalid/a"}),
        case(bindings=[]),
        case(inputs={"expert_framework": 42}),
    ],
)
def test_invalid_fixtures_rejected(bad):
    with pytest.raises(ValueError):
        render_matrix([bad])


def test_limits_and_duplicates(registered):
    for kwargs in [{"max_cases": True}, {"max_output_bytes": 1}]:
        with pytest.raises(ValueError):
            render_matrix([case()], **kwargs)
    with pytest.raises(ValueError):
        render_matrix([case(), case()])
    with pytest.raises(ValueError):
        render_matrix([case(), case(id="b")], max_cases=1)


def fixture_file(tmp_path):
    path = tmp_path / "fixture.json"
    (tmp_path / "prompt.yaml").write_text(
        'instruction: "Hello {name}"\nmetadata:\n  version: matrix.v1\n', encoding="utf-8"
    )
    fixture = {
        "version": 1,
        "prompts": [
            {
                "path": "prompt.yaml",
            }
        ],
        "cases": [case(bindings={"name": "Ada"})],
    }
    path.write_text(json.dumps(fixture), encoding="utf-8")
    return path, fixture


def run_cli(fixture, baseline, *args):
    return subprocess.run(
        [
            sys.executable,
            "-X",
            "utf8",
            "-m",
            "agentuniverse.prompt.regression_matrix",
            str(fixture),
            str(baseline),
            *args,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_cli_requires_explicit_update_and_checks_without_writes(tmp_path):
    path, fixture = fixture_file(tmp_path)
    baseline = tmp_path / "golden.json"
    assert run_cli(path, baseline).returncode != 0
    assert not baseline.exists()
    result = run_cli(path, baseline, "--update")
    assert result.returncode == 0, result.stderr
    before = baseline.read_bytes()
    result = run_cli(path, baseline)
    assert result.returncode == 0, result.stderr
    fixture["cases"][0]["bindings"]["name"] = "Grace"
    path.write_text(json.dumps(fixture), encoding="utf-8")
    result = run_cli(path, baseline)
    assert result.returncode == 1
    assert "Grace" in result.stdout
    assert baseline.read_bytes() == before
    fixture["cases"][0]["bindings"] = {}
    path.write_text(json.dumps(fixture), encoding="utf-8")
    assert run_cli(path, baseline, "--update").returncode != 0
    assert baseline.read_bytes() == before


def test_cli_rejects_duplicate_prompt_and_same_output(tmp_path):
    path, fixture = fixture_file(tmp_path)
    assert run_cli(path, path, "--update").returncode != 0
    fixture["prompts"].append(copy.deepcopy(fixture["prompts"][0]))
    path.write_text(json.dumps(fixture), encoding="utf-8")
    baseline = tmp_path / "golden.json"
    assert run_cli(path, baseline, "--update").returncode != 0
    assert not baseline.exists()


def test_cli_detects_real_yaml_edit(tmp_path):
    path, _ = fixture_file(tmp_path)
    baseline = tmp_path / "golden.json"
    assert run_cli(path, baseline, "--update").returncode == 0
    before = baseline.read_bytes()
    prompt_path = tmp_path / "prompt.yaml"
    prompt_path.write_text(prompt_path.read_text(encoding="utf-8").replace("Hello", "你好"), encoding="utf-8")
    result = run_cli(path, baseline)
    assert result.returncode == 1 and "你好" in result.stdout
    assert baseline.read_bytes() == before


@pytest.mark.parametrize(
    "text",
    [
        "instruction: a\ninstruction: b\n",
        "instruction: '${SECRET}'\n",
        "meta_class: malicious.Code\n",
        "instruction: text\nmetadata:\n  class: CustomPrompt\n",
    ],
)
def test_cli_rejects_ambiguous_or_dynamic_yaml(tmp_path, text):
    path, _ = fixture_file(tmp_path)
    (tmp_path / "prompt.yaml").write_text(text, encoding="utf-8")
    baseline = tmp_path / "golden.json"
    assert run_cli(path, baseline, "--update").returncode != 0
    assert not baseline.exists()
