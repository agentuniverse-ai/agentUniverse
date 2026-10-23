"""Reproduce this feature's scoped local tests; this is not whole-project CI."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


def main():
    here = Path(__file__).resolve().parent
    repo = here.parents[2]
    manifest = json.loads((here / "manifest.json").read_text(encoding="utf-8"))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", choices=("3.10", "3.12"), default="3.12")
    parser.add_argument("--variant", choices=tuple(manifest["variants"]), default="default")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    requirement = here / manifest["variants"][args.variant]
    prefix = ["uv", "run", "--no-project", "--python", args.python,
              "--with-requirements", str(requirement)]
    if args.dry_run:
        print(json.dumps({"cwd": str(repo), "command_prefix": prefix,
                          "tests": manifest["tests"],
                          "required_environment_names": manifest["required_environment"]}, indent=2))
        return 0
    if not shutil.which("uv"):
        parser.error("Install uv first; see https://docs.astral.sh/uv/getting-started/installation/")
    missing = [name for name in manifest["required_environment"] if not os.getenv(name)]
    if missing:
        parser.error("Configure disposable local test services first: " + ", ".join(missing))
    output = args.output_dir or Path(tempfile.mkdtemp(prefix="au-feature-tests-"))
    output = output.resolve()
    if output == here or here in output.parents:
        parser.error("Choose output outside the checked-in evidence directory")
    output.mkdir(parents=True, exist_ok=True)
    if any((output / name).exists() for name in ("junit.xml", "environment.json", "pytest.log", "summary.json")):
        parser.error("Use a fresh output directory; previous evidence will not be overwritten")
    environment = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHONUTF8="1")
    environment.update(manifest.get("environment_defaults", {}))
    version_code = (
        "import sys,json,importlib.metadata as m;"
        "print(json.dumps({'python':sys.version,'packages':"
        "{d.metadata['Name']:d.version for d in m.distributions()}},sort_keys=True))"
    )
    # Arguments come from the checked-in manifest and validated CLI choices; no shell.
    version_result = subprocess.run([*prefix, "python", "-c", version_code], cwd=repo,  # noqa: S603
                                    env=environment, capture_output=True, text=True, encoding="utf-8")
    if version_result.returncode:
        print(version_result.stderr, file=sys.stderr)
        return version_result.returncode
    (output / "environment.json").write_text(version_result.stdout, encoding="utf-8")
    command = [*prefix, "python", "-m", "pytest", "-q", *manifest["tests"],
                        "--import-mode=importlib", "--tb=short",
                        "--junitxml", str(output / "junit.xml")]
    result = subprocess.run(command, cwd=repo, env=environment,  # noqa: S603
                            capture_output=True, text=True, encoding="utf-8")
    (output / "pytest.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    summary = {"feature": manifest["feature"], "python_requested": args.python,
               "variant": args.variant, "exit_code": result.returncode,
               "scope": "local targeted tests plus selected existing regressions; not hosted CI"}
    if (output / "junit.xml").exists():
        # Only parse the local report just emitted by this test invocation.
        root = ET.parse(output / "junit.xml").getroot()  # noqa: S314
        suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
        summary.update({key: sum(int(s.get(key, "0")) for s in suites)
                        for key in ("tests", "failures", "errors", "skipped")})
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("Evidence directory: " + str(output))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
