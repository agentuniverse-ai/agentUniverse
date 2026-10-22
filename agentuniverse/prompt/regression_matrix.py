"""Offline regression snapshots using the actual Agent prompt assembly path."""

import argparse
import copy
import difflib
import json
import os
import tempfile
from pathlib import Path

import yaml

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.base.config.component_configer.configers.prompt_configer import PromptConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager


class _PromptLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in result:
                raise ValueError("duplicate or non-string YAML key")
            result[key] = self.construct_object(value_node, deep=deep)
        return result


class _MatrixAgent(Agent):
    """Only process_prompt is used; no planner/provider is constructed."""

    def input_keys(self):
        return []

    def output_keys(self):
        return []

    def parse_input(self, input_object, agent_input):
        raise RuntimeError("matrix agents only render prompts")

    def parse_result(self, agent_result):
        raise RuntimeError("matrix agents only render prompts")


def _encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def render_matrix(cases, *, max_cases=500, max_output_bytes=4_194_304):
    """Render explicitly approved fixture cases against registered Prompt versions.

    Each case has a unique id, profile, inputs and optional bindings. Profile uses
    the actual Agent inheritance fields (introduction/target/instruction and
    prompt_version). Inputs may include expert_framework, image_urls, audio_url.
    Bindings are separate template variables. Remote media references are retained
    without fetching; local file media is rejected. Returns deterministic rows
    with rendered messages or a missing-variable/render-error status.

    This does not call an LLM or judge prompt quality. Run in a dedicated test
    process with a stable PromptManager registry. Fixtures/snapshots may contain
    sensitive content: only use data approved for storing in golden files.
    """
    for limit in (max_cases, max_output_bytes):
        if type(limit) is not int or limit <= 0:
            raise ValueError("limits must be positive integers")
    rows, seen, total = [], set(), 0
    for index, original in enumerate(cases):
        if index >= max_cases or not isinstance(original, dict):
            raise ValueError("case limit or invalid case")
        if not {"id", "profile", "inputs"} <= original.keys() or not set(original) <= {
            "id",
            "profile",
            "inputs",
            "bindings",
        }:
            raise ValueError("invalid case fields")
        # Require plain JSON fixtures and isolate mutable values from runtime.
        case = json.loads(_encode(original))
        key = case["id"]
        if not isinstance(key, str) or not key or key in seen:
            raise ValueError("invalid or duplicate case ID")
        seen.add(key)
        profile, inputs, bindings = case["profile"], case["inputs"], case.get("bindings", {})
        if not all(isinstance(value, dict) for value in (profile, inputs, bindings)):
            raise ValueError("profile, inputs and bindings must be objects")
        if not set(profile) <= {"prompt_version", "introduction", "target", "instruction"}:
            raise ValueError("unsupported profile field")
        if any(value is not None and not isinstance(value, str) for value in profile.values()):
            raise ValueError("profile values must be strings or null")
        if not set(inputs) <= {"expert_framework", "image_urls", "audio_url"}:
            raise ValueError("unsupported prompt input field")
        urls = inputs.get("image_urls", [])
        if not isinstance(urls, list):
            raise ValueError("image_urls must be a list")
        for value in urls:
            url = value.get("url") if isinstance(value, dict) else value
            if not isinstance(url, str) or not url.startswith(("https://", "http://")):
                raise ValueError("matrix media must use explicit HTTP(S) references; no local file reads")
        audio = inputs.get("audio_url")
        if audio and (not isinstance(audio, str) or not audio.startswith(("https://", "http://"))):
            raise ValueError("audio must be an HTTP(S) reference")
        if "expert_framework" in inputs and not isinstance(inputs["expert_framework"], str):
            raise ValueError("expert_framework must be a string")
        row = dict(id=key)
        version = profile.get("prompt_version")
        if version and PromptManager().get_instance_obj(version) is None:
            row.update(status="missing_prompt", prompt_version=version)
        else:
            try:
                agent = _MatrixAgent()
                agent.agent_model = AgentModel(profile=copy.deepcopy(profile))
                template = agent.process_prompt(copy.deepcopy(inputs)).as_langchain()
                missing = sorted(set(template.input_variables) - bindings.keys())
                if missing:
                    row.update(status="missing_variables", missing=missing)
                else:
                    messages = template.format_messages(**bindings)
                    row.update(
                        status="rendered", messages=[dict(role=msg.type, content=msg.content) for msg in messages]
                    )
            except Exception as exc:
                # Do not include exception strings which may quote fixture values.
                row.update(status="render_error", error_type=type(exc).__name__)
        total += len(_encode(row).encode("utf-8"))
        if total > max_output_bytes:
            raise ValueError("rendered output byte limit exceeded")
        rows.append(row)
    return dict(version=1, cases=sorted(rows, key=lambda row: row["id"]))


def compare_baseline(snapshot, baseline):
    """Return deterministic golden differences; never updates the baseline."""
    for value in (snapshot, baseline):
        if (
            not isinstance(value, dict)
            or set(value) != {"version", "cases"}
            or type(value["version"]) is not int
            or value["version"] != 1
            or not isinstance(value["cases"], list)
        ):
            raise ValueError("unsupported snapshot format")
    old, new = _encode(baseline), _encode(snapshot)
    errors = [row["id"] for row in snapshot["cases"] if row["status"] != "rendered"]
    return dict(
        matches=old == new and not errors,
        failed_cases=errors,
        diff="".join(
            difflib.unified_diff(
                old.splitlines(keepends=True), new.splitlines(keepends=True), fromfile="baseline", tofile="current"
            )
        ),
    )


def _read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    with Path(path).open("rb") as stream:
        data = stream.read(4_194_305)
    if len(data) > 4_194_304:
        raise ValueError("fixture byte limit exceeded")
    return json.loads(data, object_pairs_hook=unique)


def _update(path, snapshot):
    if any(row["status"] != "rendered" for row in snapshot["cases"]):
        raise ValueError("refusing to bless failed rendering")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent, delete=False, mode="w", encoding="utf-8", newline="\n"
        ) as stream:
            temporary = Path(stream.name)
            stream.write(_encode(snapshot))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    """Run a JSON fixture; only --update authorizes replacing a golden file.

    Fixture: {version: 1, prompts: [{path}], cases: [...]}. YAML paths are relative
    to the fixture file. Only literal built-in Prompt configs are supported.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()
    if args.fixture.resolve() == args.baseline.resolve():
        raise ValueError("fixture and baseline must differ")
    fixture = _read_json(args.fixture)
    if (
        not isinstance(fixture, dict)
        or set(fixture) != {"version", "prompts", "cases"}
        or type(fixture["version"]) is not int
        or fixture["version"] != 1
    ):
        raise ValueError("unsupported matrix fixture")
    if not isinstance(fixture["prompts"], list) or len(fixture["prompts"]) > 500:
        raise ValueError("invalid prompt fixture list")
    manager = PromptManager()
    previous = dict(manager._instance_obj_map)
    try:
        for item in fixture["prompts"]:
            if not isinstance(item, dict) or set(item) != {"path"} or not isinstance(item["path"], str):
                raise ValueError("invalid prompt fixture")
            prompt_path = (args.fixture.parent / item["path"]).resolve()
            if prompt_path == args.baseline.resolve():
                raise ValueError("baseline must not overwrite a prompt file")
            with prompt_path.open("rb") as stream:
                raw = stream.read(1_048_577)
            if len(raw) > 1_048_576:
                raise ValueError("prompt file byte limit exceeded")
            values = yaml.load(raw, Loader=_PromptLoader)
            if not isinstance(values, dict) or not set(values) <= {"introduction", "target", "instruction", "metadata"}:
                raise ValueError("only literal Prompt fields are supported")
            for key, value in values.items():
                if key != "metadata" and (not isinstance(value, str) or "${" in value or "@FUNC" in value):
                    raise ValueError("prompt text must be literal strings")
            metadata = values.get("metadata", {})
            if (
                not isinstance(metadata, dict)
                or not set(metadata) <= {"type", "module", "class", "version"}
                or metadata.get("type", "PROMPT") != "PROMPT"
                or metadata.get("module", "agentuniverse.prompt.prompt") != "agentuniverse.prompt.prompt"
                or metadata.get("class", "Prompt") != "Prompt"
            ):
                raise ValueError("only built-in Prompt metadata is supported")
            config = Configer(str(prompt_path))
            config.value = values
            prompt = Prompt().initialize_by_component_configer(PromptConfiger().load_by_configer(config))
            version = prompt.get_instance_code()
            if not isinstance(version, str) or not version or manager.get_instance_obj(version) is not None:
                raise ValueError("missing or duplicate prompt version")
            manager.register(version, prompt)
        snapshot = render_matrix(fixture["cases"])
        if args.update:
            _update(args.baseline, snapshot)
            print(_encode(dict(updated=True, cases=len(snapshot["cases"]))))
            return 0
        report = compare_baseline(snapshot, _read_json(args.baseline))
        print(_encode(report))
        return 0 if report["matches"] else 1
    finally:
        manager._instance_obj_map.clear()
        manager._instance_obj_map.update(previous)


if __name__ == "__main__":
    raise SystemExit(main())
