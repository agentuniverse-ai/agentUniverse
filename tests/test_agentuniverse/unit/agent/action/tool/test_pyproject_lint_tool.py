#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_pyproject_lint_tool.py

"""Offline unit tests for PyprojectLintTool.

The tool lints pyproject.toml project metadata (PEP 621) purely
on the standard library (tomllib) and never touches the network,
so this suite runs fully offline. Every assertion is deterministic
against hand-computed ground truths: the ``lint`` vectors trigger
every rule plus a clean all-valid control, the Poetry-style
fixture is the repository's own pyproject.toml content verbatim
(mapped best-effort, never an error), the ``project_summary``
vectors cover the arithmetic (dependency / entry-point counts,
optional groups, the requires-python min/max bound matrix for
>= / <= / == / ~= / != clauses and the Poetry caret conversion)
and the error matrix walks every parameter-level ValueError.
Findings order is asserted deterministic (file-level first, then
field, code, message).

When the third-party ``packaging`` distribution is importable, a
differential suite additionally compares the PEP 440 version
grammar and the requires-python specifier grammar against
``packaging.version.Version`` / ``packaging.specifiers.SpecifierSet``
over hundreds of seeded strings — accepted-by-them must be
valid-for-us and rejected-by-them must be invalid-for-us (skipped
when ``packaging`` is absent, so the suite stays stdlib-only).
"""

import random
import unittest

from agentuniverse.agent.action.tool.common_tool import (
    PyprojectLintTool,
)
from agentuniverse.agent.action.tool.common_tool.pyproject_lint_tool \
    import PyprojectLintTool as DirectPyprojectLintTool


def run_lint(pyproject, available_files=None):
    return PyprojectLintTool().execute(
        mode="lint", pyproject=pyproject, available_files=available_files
    )


def run_summary(pyproject):
    return PyprojectLintTool().execute(
        mode="project_summary", pyproject=pyproject
    )


def codes(result):
    return [finding["code"] for finding in result["findings"]]


# A complete, valid [build-system] block — fixtures that should
# stay free of the build_system_missing info prepend it.
BS = (
    '[build-system]\n'
    'requires = ["hatchling"]\n'
    'build-backend = "hatchling.build"\n'
)


CLEAN = BS + '''
[project]
name = "demo-package"
version = "1.0.0rc1"
description = "A demonstration package"
readme = "README.md"
requires-python = ">=3.10,<4"
license = "MIT OR Apache-2.0"
authors = [
    { name = "Ada Lovelace", email = "ada@example.com" },
    { email = "grace@example.org" },
]
maintainers = [{ name = "Maint One" }]
keywords = ["demo", "packaging"]
classifiers = [
    "Programming Language :: Python :: 3.10",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
]
dependencies = [
    "requests>=2.28,<3",
    "zope.interface[security]~=5.0 ; python_version < '3.11'",
    "direct @ https://example.com/direct-1.0-py3-none-any.whl",
]

[project.optional-dependencies]
test = ["pytest>=7", "Foo_Bar==1.0"]
docs = ["sphinx"]

[project.urls]
Homepage = "https://example.com"
Repository = "https://github.com/example/demo"

[project.scripts]
demo-cli = "demo_package.cli:main"

[project.gui-scripts]
demo-gui = "demo_package.gui:run"

[project.entry-points."demo.plugins"]
plugin-a = "demo_package.plugins.a:register"
'''

CLEAN_FILES = ["README.md", "src/demo", "./pyproject.toml"]

# The repository's own pyproject.toml (Poetry layout), verbatim.
POETRY_FIXTURE = '''[tool.poetry]
name = "agentUniverse"
version = "0.0.19"
description = "agentUniverse is a framework for developing applications powered by multi-agent base on large language model."

authors = ["AntGroup <jerry.zzw@antgroup.com>"]
repository = "https://github.com/agentuniverse-ai/agentUniverse"
readme = "README_PYPI.md"

packages = [
    { include = "agentuniverse" },
    { include = "agentuniverse_connector" },
    { include = "agentuniverse_extension" },
    { include = "agentuniverse_product" },
]
include = ["*.yaml"]
classifiers = [
    "Programming Language :: Python :: 3.10",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
]

[tool.poetry.dependencies]
python = "^3.10"
requests = "^2.32.0"
cffi = "^1.15.1"
flask = "^2.3.2"
werkzeug = "^3.0.3"
langchain = "0.1.20"
langchain-core = "0.1.52"
langchain-community = "0.0.38"
openai = '1.55.3'
tiktoken = '<1.0.0'
loguru = '0.7.2'
flask_cors = '4.0.0'
SQLAlchemy = '2.0.25'
pydantic = "^2.6.4"
gunicorn = "^22.0.0"
grpcio = "1.63.0"
chromadb = "0.4.24"
opentelemetry-api = "^1.25.0"
opentelemetry-sdk = "^1.25.0"
opentelemetry-semantic-conventions = ">=0.48b0"
opentelemetry-exporter-otlp-proto-grpc = "^1.25.0"
opentelemetry-exporter-otlp-proto-http = "^1.25.0"
sphinx = "^7.2.6"
Jinja2 = "^3.1.4"
tqdm = "^4.66.3"
sphinx-rtd-theme = "^2.0.0"
aliyun-log-python-sdk = { version = "0.8.8", optional = true}
pymilvus = { version = "^2.4.3", optional = true}
psycopg = { version = "^3.2.0", extras = ["binary"], optional = true}
pgvector = { version = "^0.3.0", optional = true}
googleapis-common-protos = "^1.63.0"
myst-parser = "^2.0.0"
qianfan = "^0.3.12"
dashscope = "^1.19.1"
anthropic = "^0.26.0"
ollama = '^0.2.1'
langchain-anthropic = '^0.1.13'
numpy = '^1.26.0'
pandas = "^2.2.2"
pyarrow = "^16.1.0"
duckduckgo-search = "^6.3.5"
primp = "^0.6.5"
wikipedia= "^1.4.0"
openpyxl = "^3.1.5"
python-pptx = { version = "^1.0.2", optional = true }
python-docx = { version = "^1.1.2", optional = true }
pillow = "^10.4.0"
pypdf = { version = "^5.0.0", optional = true }
jieba = "^0.42.1"
networkx = "^3.3"
httpx = ">=0.27.2"
tomli = "^2.2"
mcp = "<1.22.0"
opentracing = ">=2.4.0,<3.0.0"
jsonlines = "^4.0.0"
EbookLib = "^0.18"
beautifulsoup4 = "^4.12.0"
redis = { version = "^5.0.0", optional = true }
# qdrant-client = "^1.15.1" unsupportable version due to numpy version limit

[tool.poetry.extras]
log_ext = ["aliyun-log-python-sdk"]
store_ext = ["pymilvus", "psycopg", "pgvector", "redis"]
office_ext = ["python-docx", "python-pptx"]
pdf_ext = ["pypdf"]

[tool.poetry.group.dev.dependencies]
pytest = "^7.2.0"
pytest-cov = "^4.0.0"
deptry = "^0.6.4"
pre-commit = "^2.20.0"


[[tool.poetry.source]]
name = "china"
url = "https://mirrors.aliyun.com/pypi/simple/"
priority = "primary"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 120
target-version = ['py310']
preview = true

[tool.mypy]
files = ["agentuniverse"]
disallow_untyped_defs = "True"
disallow_any_unimported = "True"
no_implicit_optional = "True"
check_untyped_defs = "True"
warn_return_any = "True"
warn_unused_ignores = "True"
show_error_codes = "True"

[tool.ruff]
target-version = "py310"
line-length = 120
fix = true

[tool.ruff.lint]
select = [
    # flake8-2020
    "YTT",
    # flake8-bandit
    "S",
    # flake8-bugbear
    "B",
    # flake8-builtins
    "A",
    # flake8-comprehensions
    "C4",
    # flake8-debugger
    "T10",
    # flake8-simplify
    "SIM",
    # isort
    "I",
    # mccabe
    "C90",
    # pycodestyle
    "E", "W",
    # pyflakes
    "F",
    # pygrep-hooks
    "PGH",
    # pyupgrade
    "UP",
    # ruff
    "RUF",
    # tryceratops
    "TRY",
]
ignore = [
    # LineTooLong
    "E501",
    # DoNotAssignLambda
    "E731",
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]

[tool.coverage.report]
skip_empty = true

[tool.coverage.run]
branch = true
source = ["agentuniverse"]
'''


# ------------------------------------------------------------------ #
# lint mode — every rule, plus the clean control
# ------------------------------------------------------------------ #

class LintGroundTruths(unittest.TestCase):
    """``lint`` — the rule set over hand-computed fixtures."""

    def test_clean_control(self):
        """A complete valid PEP 621 file lints to zero findings."""
        result = run_lint(CLEAN, available_files=CLEAN_FILES)
        self.assertEqual(result["findings"], [])
        self.assertEqual(
            result["counts"],
            {"findings": 0, "errors": 0, "warnings": 0, "infos": 0},
        )

    def test_missing_project_table(self):
        """No [project] and no [tool.poetry] — the one error."""
        result = run_lint(BS + '[tool.black]\nline-length = 120\n')
        self.assertEqual(codes(result), ["missing_project_table"])
        self.assertEqual(
            result["findings"][0]["severity"], "error"
        )
        self.assertIsNone(result["findings"][0]["field"])

    def test_toml_parse_error(self):
        """Unparseable text — a single error, nothing else runs."""
        result = run_lint('not [valid toml')
        self.assertEqual(codes(result), ["toml_parse_error"])
        self.assertEqual(
            result["counts"],
            {"findings": 1, "errors": 1, "warnings": 0, "infos": 0},
        )

    def test_project_not_table(self):
        """project = scalar — wrong TOML type."""
        result = run_lint('project = "x"\n\n' + BS)
        self.assertEqual(codes(result), ["project_not_table"])

    def test_tool_shape(self):
        """tool = scalar — wrong TOML type for the tool table."""
        result = run_lint(
            'tool = 3\n\n' + BS + '[project]\nname = "demo"\n'
            'version = "1.0"\n'
        )
        self.assertEqual(
            codes(result), ["description_missing", "tool_shape"]
        )

    # --- poetry layout ------------------------------------------- #

    def test_poetry_only_real_repo_file(self):
        """The repo's own Poetry pyproject — info mapping, no errors."""
        result = run_lint(POETRY_FIXTURE)
        self.assertEqual(codes(result), ["poetry_layout"])
        self.assertEqual(result["findings"][0]["severity"], "info")
        message = result["findings"][0]["message"]
        self.assertIn("name='agentUniverse'", message)
        self.assertIn("version='0.0.19'", message)
        self.assertIn("requires-python='^3.10'", message)
        self.assertIn("4 extras", message)
        self.assertIn("57 dependencies", message)
        self.assertEqual(
            result["counts"],
            {"findings": 1, "errors": 0, "warnings": 0, "infos": 1},
        )

    def test_poetry_only_minimal(self):
        """A minimal Poetry file without build-system."""
        text = (
            '[tool.poetry]\nname = "demo"\nversion = "0.1.0"\n'
            'description = "d"\n'
            '[tool.poetry.dependencies]\npython = "^3.10"\n'
            'requests = "^2.0"\n'
            '[tool.poetry.extras]\nextra1 = ["requests"]\n'
        )
        result = run_lint(text)
        self.assertEqual(
            codes(result), ["build_system_missing", "poetry_layout"]
        )
        self.assertTrue(
            all(f["severity"] == "info" for f in result["findings"])
        )

    def test_poetry_hybrid(self):
        """Both tables present — info note, full rules still run."""
        text = (
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            '[tool.poetry]\nname = "demo"\n'
        )
        result = run_lint(text)
        self.assertEqual(
            codes(result), ["poetry_layout", "description_missing"]
        )

    # --- name ------------------------------------------------------ #

    def test_name_missing(self):
        result = run_lint(BS + '[project]\nversion = "1.0"\n')
        self.assertEqual(
            codes(result), ["description_missing", "name_missing"]
        )

    def test_name_invalid(self):
        result = run_lint(
            BS + '[project]\nname = "-bad-"\nversion = "1.0"\n'
        )
        self.assertEqual(
            codes(result), ["description_missing", "name_invalid"]
        )

    def test_name_not_normalized(self):
        result = run_lint(
            BS + '[project]\nname = "agentUniverse"\nversion = "1.0"\n'
        )
        self.assertEqual(
            codes(result), ["description_missing", "name_not_normalized"]
        )
        self.assertEqual(result["findings"][0]["severity"], "info")

    # --- version ---------------------------------------------------- #

    def test_version_missing(self):
        result = run_lint(BS + '[project]\nname = "demo"\n')
        self.assertEqual(
            codes(result), ["description_missing", "version_missing"]
        )

    def test_version_invalid(self):
        for bad in ("next", "1..2", "1.0-", "1.0.0!"):
            result = run_lint(
                BS + f'[project]\nname = "demo"\nversion = "{bad}"\n'
            )
            self.assertEqual(
                codes(result),
                ["description_missing", "version_invalid"],
                bad,
            )

    def test_version_valid_matrix(self):
        for good in (
            "1.0.0rc1", "2024.10.21", "1!2.0", "1.0+local",
            "1.0-post2", "1.0.dev3", "v1.0", "0.0.19", "1.0.alpha1",
        ):
            result = run_lint(
                BS + f'[project]\nname = "demo"\nversion = "{good}"\n'
            )
            self.assertEqual(codes(result), ["description_missing"], good)

    def test_version_dynamic_suppresses_missing(self):
        result = run_lint(
            BS + '[project]\nname = "demo"\ndynamic = ["version"]\n'
        )
        self.assertEqual(codes(result), ["description_missing"])

    # --- requires-python --------------------------------------------- #

    def test_requires_python_invalid(self):
        for bad in (">=3.x", "3.10", ">=3.10.*", ">=1.0+local",
                    "~=3", ">=3.10,,<="):
            result = run_lint(
                BS + '[project]\nname = "demo"\nversion = "1.0"\n'
                f'requires-python = "{bad}"\n'
            )
            self.assertEqual(
                codes(result),
                ["description_missing", "requires_python_invalid"],
                bad,
            )

    def test_requires_python_valid_matrix(self):
        for good in ("", ">=3.10", ">= 3.10 , < 4 ", ">=3.10,",
                     "==3.10.*", "!=3.9.*", "~=3.10", ">=v3.10",
                     "==1.0+local", "===anything"):
            result = run_lint(
                BS + '[project]\nname = "demo"\nversion = "1.0"\n'
                f'requires-python = "{good}"\n'
            )
            self.assertEqual(
                codes(result), ["description_missing"], good
            )

    # --- license (PEP 639) -------------------------------------------- #

    def test_license_deprecated_table(self):
        result = run_lint(
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'license = { text = "MIT" }\n'
        )
        self.assertEqual(
            codes(result), ["description_missing", "license_deprecated_table"]
        )
        self.assertEqual(
            result["findings"][1]["severity"], "info"
        )
        self.assertIn("PEP 639", result["findings"][1]["message"])

    def test_license_shape(self):
        result = run_lint(
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'license = { }\n'
        )
        self.assertEqual(
            codes(result), ["description_missing", "license_shape"]
        )

    def test_license_file_dangling(self):
        result = run_lint(
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'license = { file = "LICENSE.txt" }\n',
            available_files=["README.md"],
        )
        self.assertEqual(
            codes(result),
            [
                "description_missing",
                "license_deprecated_table",
                "license_file_dangling",
            ],
        )

    def test_license_spdx_string_clean(self):
        result = run_lint(
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'license = "MIT OR Apache-2.0"\n'
        )
        self.assertEqual(codes(result), ["description_missing"])

    # --- readme --------------------------------------------------------- #

    def test_readme_dangling_string(self):
        result = run_lint(
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'readme = "MISSING.md"\n',
            available_files=["README.md"],
        )
        self.assertEqual(
            codes(result), ["description_missing", "readme_dangling"]
        )

    def test_readme_dangling_table(self):
        result = run_lint(
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'readme = { file = "docs/MISSING.md", '
            'content-type = "text/markdown" }\n',
            available_files=["README.md", "docs/other.md"],
        )
        self.assertEqual(
            codes(result), ["description_missing", "readme_dangling"]
        )

    def test_readme_shape(self):
        result = run_lint(
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'readme = { charset = "utf-8" }\n'
        )
        self.assertEqual(
            codes(result), ["description_missing", "readme_shape"]
        )

    def test_readme_inline_text_and_listing_skip(self):
        """Inline text needs no file; no listing means no check."""
        result = run_lint(
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'readme = { text = "hello", content-type = "text/plain" }\n'
            'readme2 = 1\n',
            available_files=None,
        )
        self.assertEqual(codes(result), ["description_missing"])
        result = run_lint(
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'readme = "README.md"\n'
        )
        self.assertEqual(codes(result), ["description_missing"])
        self.assertIn("available_files listing (None supplied",
                      result["note"])

    def test_description_missing_info(self):
        result = run_lint(
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'dynamic = ["description"]\n'
        )
        self.assertEqual(result["findings"], [])

    # --- authors / maintainers ------------------------------------------- #

    def test_authors_maintainers_shapes(self):
        base = (
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
        )
        result = run_lint(base + 'authors = "Ada"\n')
        self.assertEqual(codes(result), ["authors_shape"])
        result = run_lint(base + 'authors = ["Ada"]\n')
        self.assertEqual(codes(result), ["authors_shape"])
        result = run_lint(base + 'authors = [{ }]\n')
        self.assertEqual(codes(result), ["authors_shape"])
        result = run_lint(
            base + 'authors = [{ name = "", email = "a@b.io" }]\n'
        )
        self.assertEqual(codes(result), ["authors_shape"])
        result = run_lint(
            base + 'authors = [{ name = "Ada", email = "not-an-email" }]\n'
        )
        self.assertEqual(codes(result), ["authors_shape"])
        self.assertIn("email", result["findings"][0]["message"])
        result = run_lint(
            base + 'maintainers = [{ email = "no-at-sign.io" }]\n'
        )
        self.assertEqual(codes(result), ["maintainers_shape"])

    def test_authors_valid_matrix(self):
        result = run_lint(
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
            'authors = [{ name = "Ada" }, { email = "g@x.org" }, '
            '{ name = "A B", email = "a.b+c@x.co.uk" }]\n'
            'maintainers = [{ name = "Only Name" }]\n'
        )
        self.assertEqual(result["findings"], [])

    # --- keywords / classifiers / urls ------------------------------------ #

    def test_keywords_shape(self):
        base = (
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
        )
        result = run_lint(base + 'keywords = "demo"\n')
        self.assertEqual(codes(result), ["keywords_shape"])
        result = run_lint(base + 'keywords = ["a", 1]\n')
        self.assertEqual(codes(result), ["keywords_shape"])
        result = run_lint(base + 'keywords = ["a", ""]\n')
        self.assertEqual(codes(result), ["keywords_shape"])

    def test_classifiers_shape_and_unknown(self):
        base = (
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
        )
        result = run_lint(base + 'classifiers = ["License :: OSI"\n')
        self.assertEqual(codes(result), ["toml_parse_error"])
        result = run_lint(base + 'classifiers = [1]\n')
        self.assertEqual(codes(result), ["classifiers_shape"])
        result = run_lint(base + 'classifiers = ["Nonsense :: Foo"]\n')
        self.assertEqual(codes(result), ["classifier_unknown"])
        self.assertEqual(result["findings"][0]["severity"], "info")
        result = run_lint(
            base + 'classifiers = [\n'
            '  "Programming Language :: Python :: 3.10",\n'
            '  "License :: OSI Approved :: Apache Software License",\n'
            '  "Operating System :: OS Independent",\n'
            '  "Topic :: Software Development",\n'
            '  "Private :: Do Not Upload",\n'
            ']\n'
        )
        self.assertEqual(result["findings"], [])

    def test_urls_shape(self):
        base = (
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
        )
        result = run_lint(
            base + '[project.urls]\nHomepage = 3\n'
        )
        self.assertEqual(codes(result), ["urls_shape"])
        result = run_lint(
            base + '[project.urls]\nHomepage = "https://x.io"\n'
            'Changelog = "https://x.io/news"\n'
        )
        self.assertEqual(result["findings"], [])

    # --- dependencies / optional-dependencies ------------------------------ #

    def test_dependencies_shape_and_invalid(self):
        base = (
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
        )
        result = run_lint(base + 'dependencies = "requests"\n')
        self.assertEqual(codes(result), ["dependencies_shape"])
        result = run_lint(base + 'dependencies = [1]\n')
        self.assertEqual(codes(result), ["dependencies_shape"])
        result = run_lint(base + 'dependencies = [">=1.0"]\n')
        self.assertEqual(codes(result), ["dependency_invalid"])
        result = run_lint(base + 'dependencies = ["no name here =="]\n')
        self.assertEqual(codes(result), ["dependency_invalid"])
        result = run_lint(base + 'dependencies = ["foo~=1"]\n')
        self.assertEqual(codes(result), ["dependency_invalid"])

    def test_dependencies_valid_matrix(self):
        """PEP 508 forms pip accepts (packaging-aligned clauses)."""
        result = run_lint(
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
            'dependencies = [\n'
            '  "requests >= 2.28, < 3 ; python_version < \'3.11\'",\n'
            '  "zope.interface[security]~=5.0,",\n'
            '  "foo==1.2.*",\n'
            '  "bar===whatever!!",\n'
            '  "direct @ https://example.com/x.whl",\n'
            '  "plain",\n'
            '  "old-setuptools (>=1.0, <2)",\n'
            '  "no-clauses ()",\n'
            '  "empty-extras[]",\n'
            '  "spaced-extras[ e1 , e2 ]",\n'
            '  "local-pin==1.0+abc.def",\n'
            ']\n'
        )
        self.assertEqual(result["findings"], [])

    def test_dependency_parenthesized_clause_list(self):
        """PEP 508's parenthesized specifier spelling (regression:
        previously reported dependency_invalid)."""
        base = (
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
        )
        for dep in (
            "Cython (>=0.29)",
            "pip ( >=1.0, <2 )",
            "foo (); python_version < '4'",
            "foo(>=1.0,)",
        ):
            result = run_lint(
                base + f'dependencies = ["{dep}"]\n'
            )
            self.assertEqual(result["findings"], [], dep)
        # Unbalanced parentheses stay invalid.
        result = run_lint(base + 'dependencies = ["foo(>=1.0"]\n')
        self.assertEqual(codes(result), ["dependency_invalid"])
        result = run_lint(base + 'dependencies = ["foo>=1.0)"]\n')
        self.assertEqual(codes(result), ["dependency_invalid"])

    def test_dependency_clauses_packaging_aligned(self):
        """Clause rules pip enforces (regression: previously all
        accepted by the loose grammar)."""
        base = (
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
        )
        for dep in (
            "foo>=1.*",       # wildcard on >=
            "foo~=1.0.*",     # wildcard on ~=
            "foo==abc",       # non-PEP 440 token on ==
            "foo!=abc",
            "foo<1.0+local",  # local segment on <
            "foo~=1.0+local",  # local segment on ~=
            "foo>=1.0,,<2",   # empty clause between commas
            "foo ===",        # bare === — packaging's empty-string
                              # arbitrary-equality quirk, rejected
        ):
            result = run_lint(base + f'dependencies = ["{dep}"]\n')
            self.assertEqual(codes(result), ["dependency_invalid"], dep)
        # The adjacent legal forms stay clean.
        for dep in (
            "foo==1.*", "foo!=1.0.*", "foo==1.0+local",
            "foo!=1.0+local", "foo===whatever!!", "foo>=1.0,",
            "foo==1!2.0", "foo~=1.0rc1",
        ):
            result = run_lint(base + f'dependencies = ["{dep}"]\n')
            self.assertEqual(result["findings"], [], dep)

    def test_extras_grammar(self):
        """Extras entries: PEP 508 charset, no empty names."""
        base = (
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
        )
        for dep in ("foo[e1,]", "foo[e1,,e2]", "foo[,x]", "foo[e1!x]"):
            result = run_lint(base + f'dependencies = ["{dep}"]\n')
            self.assertEqual(codes(result), ["dependency_invalid"], dep)
        for dep in ("foo[]", "foo[ ]", "foo[e1,e2]", "foo[a-b_c.d]"):
            result = run_lint(base + f'dependencies = ["{dep}"]\n')
            self.assertEqual(result["findings"], [], dep)

    def test_duplicate_dependency_after_normalization(self):
        result = run_lint(
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
            'dependencies = ["Foo_bar", "foo-bar", "foo.bar"]\n'
        )
        dupes = [
            f for f in result["findings"]
            if f["code"] == "duplicate_dependency"
        ]
        self.assertEqual(len(dupes), 2)
        self.assertTrue(all(f["severity"] == "warning" for f in dupes))
        self.assertEqual(result["counts"]["warnings"], 2)

    def test_optional_dependencies_matrix(self):
        base = (
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
        )
        result = run_lint(base + 'optional-dependencies = ["test"]\n')
        self.assertEqual(codes(result), ["optional_dependencies_shape"])
        result = run_lint(
            base + '[project.optional-dependencies]\n'
            'test = "pytest"\n'
        )
        self.assertEqual(codes(result), ["optional_group_shape"])
        result = run_lint(
            base + '[project.optional-dependencies]\n'
            'test = ["pytest", "bad name"]\n'
        )
        self.assertEqual(codes(result), ["optional_dependency_invalid"])
        self.assertEqual(
            result["findings"][0]["field"], "optional-dependencies.test"
        )
        result = run_lint(
            base + '[project.optional-dependencies]\n'
            'test = ["pytest>=7", "pytest<9"]\n'
        )
        self.assertEqual(codes(result), ["duplicate_dependency"])

    def test_dependency_overlap(self):
        result = run_lint(
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
            'dependencies = ["requests>=2"]\n'
            '[project.optional-dependencies]\n'
            'test = ["Requests[security]>=1"]\n'
            'docs = ["sphinx"]\n'
        )
        overlaps = [
            f for f in result["findings"]
            if f["code"] == "dependency_overlap"
        ]
        self.assertEqual(len(overlaps), 1)
        self.assertEqual(overlaps[0]["severity"], "warning")
        self.assertIn("requests", overlaps[0]["message"])
        # Cross-group repetition is deliberately not flagged.
        result = run_lint(
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
            '[project.optional-dependencies]\n'
            'test = ["sphinx"]\n'
            'docs = ["sphinx"]\n'
        )
        self.assertEqual(result["findings"], [])

    # --- dynamic ------------------------------------------------------------ #

    def test_dynamic_rules(self):
        base = (
            BS + '[project]\nname = "demo"\ndescription = "d"\n'
        )
        result = run_lint(base + 'dynamic = "version"\n')
        self.assertEqual(
            codes(result), ["dynamic_shape", "version_missing"]
        )
        result = run_lint(base + 'dynamic = ["not-a-field"]\n')
        self.assertEqual(
            codes(result),
            ["dynamic_unknown_field", "version_missing"],
        )
        self.assertEqual(
            result["findings"][0]["severity"], "warning"
        )
        result = run_lint(
            base + 'dynamic = ["version"]\nversion = "next"\n'
        )
        self.assertEqual(codes(result), ["dynamic_conflict"])
        self.assertEqual(result["findings"][0]["severity"], "error")
        result = run_lint(base + 'dynamic = ["version"]\n')
        self.assertEqual(result["findings"], [])

    # --- scripts / gui-scripts / entry-points --------------------------------- #

    def test_scripts_rules(self):
        base = (
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
        )
        result = run_lint(base + '[project.scripts]\ndemo = 1\n')
        self.assertEqual(codes(result), ["scripts_shape"])
        result = run_lint(
            base + '[project.scripts]\n"bad name!" = "mod:fn"\n'
        )
        self.assertEqual(codes(result), ["script_name_invalid"])
        result = run_lint(
            base + '[project.scripts]\ndemo = "mod fn"\n'
        )
        self.assertEqual(codes(result), ["entry_point_target_invalid"])
        result = run_lint(
            base + '[project.gui-scripts]\ndemo-gui = ":fn"\n'
        )
        self.assertEqual(codes(result), ["entry_point_target_invalid"])

    def test_scripts_valid_matrix(self):
        result = run_lint(
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
            '[project.scripts]\n'
            'demo-cli = "demo_package.cli:main"\n'
            'alt = "demo_package.cli:Class.method"\n'
            'extra = "demo_package.cli:main [test]"\n'
            'module-only = "demo_package.cli"\n'
            '[project.gui-scripts]\ndemo-gui = "demo.gui:run"\n'
        )
        self.assertEqual(result["findings"], [])

    def test_entry_points_rules(self):
        base = (
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
        )
        result = run_lint(base + 'entry-points = "x"\n')
        self.assertEqual(codes(result), ["entry_points_shape"])
        result = run_lint(
            base + '[project.entry-points."demo.plugins"]\na = 1\n'
        )
        self.assertEqual(codes(result), ["entry_points_shape"])
        self.assertEqual(
            result["findings"][0]["field"], "entry-points.demo.plugins"
        )
        result = run_lint(
            base + '[project.entry-points."demo.plugins"]\n'
            'plugin-a = "not a target!"\n'
        )
        self.assertEqual(codes(result), ["entry_point_target_invalid"])
        result = run_lint(
            base + '[project.entry-points."demo.plugins"]\n'
            'plugin-a = "demo.plugins.a:register"\n'
        )
        self.assertEqual(result["findings"], [])

    # --- build-system ----------------------------------------------------------- #

    def test_build_system_rules(self):
        result = run_lint(
            '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
        )
        self.assertEqual(codes(result), ["build_system_missing"])
        self.assertEqual(result["findings"][0]["severity"], "info")
        result = run_lint(
            '[build-system]\nrequires = "setuptools"\n'
            'build-backend = "setuptools.build_meta"\n'
            '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
        )
        self.assertEqual(codes(result), ["build_system_shape"])
        result = run_lint(
            '[build-system]\nrequires = ["setuptools"]\n'
            'build-backend = 1\n'
            '[project]\nname = "demo"\nversion = "1.0"\n'
            'description = "d"\n'
        )
        self.assertEqual(codes(result), ["build_system_shape"])

    # --- determinism --------------------------------------------------------------- #

    def test_ordering_and_determinism(self):
        """File-level first, then field / code / message; stable."""
        messy = (
            '[project]\n'
            'name = "-bad-"\n'
            'version = "next"\n'
            'dependencies = ["bad name"]\n'
            '[project.optional-dependencies]\n'
            'test = ["also bad"]\n'
            '[project.scripts]\n'
            '"x!" = "y"\n'
        )
        first = run_lint(messy)
        second = run_lint(messy)
        self.assertEqual(first, second)
        fields = [
            (0 if f["field"] is None else 1, f["field"] or "")
            for f in first["findings"]
        ]
        self.assertEqual(fields, sorted(fields))
        counts = first["counts"]
        self.assertEqual(
            counts["findings"],
            counts["errors"] + counts["warnings"] + counts["infos"],
        )


# ------------------------------------------------------------------ #
# project_summary mode — the arithmetic
# ------------------------------------------------------------------ #

class SummaryGroundTruths(unittest.TestCase):
    """``project_summary`` — counts, groups, bounds, layouts."""

    def test_pep621_summary(self):
        result = run_summary(CLEAN)
        self.assertEqual(result["layout"], "pep621")
        self.assertEqual(result["name"], "demo-package")
        self.assertEqual(result["version"], "1.0.0rc1")
        self.assertEqual(result["requires_python"], ">=3.10,<4")
        self.assertEqual(result["dependency_count"], 3)
        self.assertEqual(result["optional_groups"], ["docs", "test"])
        self.assertEqual(
            result["python_requires_range"], {"min": "3.10", "max": "4"}
        )
        self.assertEqual(result["entry_points_count"], 3)
        self.assertEqual(result["dynamic_fields"], [])

    def test_range_matrix(self):
        def bounds(spec):
            return run_summary(
                BS + '[project]\nname = "demo"\nversion = "1.0"\n'
                f'requires-python = "{spec}"\n'
            )["python_requires_range"]

        self.assertEqual(bounds(">=3.10,<4"), {"min": "3.10", "max": "4"})
        self.assertEqual(bounds("~=3.10"), {"min": "3.10", "max": "4.0"})
        self.assertEqual(
            bounds("~=2.2.1"), {"min": "2.2.1", "max": "2.3.0"}
        )
        self.assertEqual(bounds("==3.11"), {"min": "3.11", "max": "3.11"})
        self.assertEqual(bounds(">3.9"), {"min": "3.9", "max": None})
        self.assertEqual(bounds("<=3.12"), {"min": None, "max": "3.12"})
        self.assertEqual(
            bounds("!=3.9.*,>=3.10"), {"min": "3.10", "max": None}
        )
        self.assertEqual(bounds(">3.8,>3.9"), {"min": "3.9", "max": None})
        self.assertEqual(bounds("<4,<3.13"), {"min": None, "max": "3.13"})
        self.assertEqual(bounds(""), None)

    def test_poetry_summary_real_repo_file(self):
        """The repo's own Poetry pyproject, mapped best-effort."""
        result = run_summary(POETRY_FIXTURE)
        self.assertEqual(result["layout"], "poetry")
        self.assertEqual(result["name"], "agentUniverse")
        self.assertEqual(result["version"], "0.0.19")
        self.assertEqual(result["requires_python"], "^3.10")
        self.assertEqual(result["dependency_count"], 57)
        self.assertEqual(
            result["optional_groups"],
            ["log_ext", "office_ext", "pdf_ext", "store_ext"],
        )
        self.assertEqual(
            result["python_requires_range"],
            {"min": "3.10", "max": "4.0"},
        )
        self.assertEqual(result["entry_points_count"], 0)
        self.assertEqual(result["dynamic_fields"], [])
        self.assertIn("poetry", result["note"].lower())

    def test_poetry_summary_minimal_and_caret_edges(self):
        text = (
            '[tool.poetry]\nname = "demo"\nversion = "0.1.0"\n'
            '[tool.poetry.dependencies]\npython = "^0.10"\n'
            'a = "1"\n'
        )
        result = run_summary(text)
        self.assertEqual(result["dependency_count"], 1)
        self.assertEqual(
            result["python_requires_range"], {"min": "0.10", "max": "0.11"}
        )
        text = (
            '[tool.poetry]\nname = "demo"\nversion = "0.1.0"\n'
            '[tool.poetry.dependencies]\npython = ">=3.9,<3.13"\n'
        )
        result = run_summary(text)
        self.assertEqual(
            result["python_requires_range"], {"min": "3.9", "max": "3.13"}
        )
        text = (
            '[tool.poetry]\nname = "demo"\nversion = "0.1.0"\n'
            '[tool.poetry.dependencies]\npython = "*"\n'
            '[tool.poetry.scripts]\ndemo = "demo:main"\n'
        )
        result = run_summary(text)
        self.assertIsNone(result["python_requires_range"])
        self.assertEqual(result["entry_points_count"], 1)

    def test_none_layout_summary(self):
        result = run_summary(BS + '[tool.black]\nline-length = 120\n')
        self.assertEqual(result["layout"], "none")
        self.assertIsNone(result["name"])
        self.assertEqual(result["dependency_count"], 0)
        self.assertIsNone(result["python_requires_range"])

    def test_unparseable_summary(self):
        result = run_summary("not [valid toml")
        self.assertEqual(result["layout"], "none")
        self.assertIn("toml_parse_error", result["note"])

    def test_dynamic_and_invalid_counts_summary(self):
        """dynamic fields listed; bad entries not counted."""
        result = run_summary(
            BS + '[project]\nname = "demo"\nversion = "1.0"\n'
            'dependencies = ["ok", 1, "also-ok"]\n'
            'dynamic = ["description", "license"]\n'
        )
        self.assertEqual(result["dependency_count"], 2)
        self.assertEqual(
            result["dynamic_fields"], ["description", "license"]
        )


# ------------------------------------------------------------------ #
# Parameter-level validation (ValueError before any computation)
# ------------------------------------------------------------------ #

class ErrorMatrix(unittest.TestCase):
    """Every malformed-parameter path raises ValueError."""

    def test_bad_mode(self):
        for mode in (None, "parse", "lints", 1, True):
            with self.assertRaises(ValueError):
                PyprojectLintTool().execute(
                    mode=mode, pyproject="[project]\n"
                )

    def test_bad_pyproject(self):
        for value in (None, 1, True, b"[project]", ["x"]):
            with self.assertRaises(ValueError):
                PyprojectLintTool().execute(mode="lint", pyproject=value)

    def test_pyproject_caps(self):
        with self.assertRaises(ValueError):
            PyprojectLintTool().execute(
                mode="lint", pyproject="x\n" * 10_001
            )
        with self.assertRaises(ValueError):
            PyprojectLintTool().execute(
                mode="lint", pyproject="x" * 10_001
            )
        with self.assertRaises(ValueError):
            PyprojectLintTool().execute(
                mode="lint", pyproject="x" * 4_000_001
            )

    def test_bad_available_files(self):
        run = lambda files: PyprojectLintTool().execute(
            mode="lint", pyproject="[project]\n", available_files=files
        )
        for value in ("README.md", 1, True, {"a": 1}):
            with self.assertRaises(ValueError):
                run(value)
        for entry in (1, True, "", "   "):
            with self.assertRaises(ValueError):
                run([entry])
        with self.assertRaises(ValueError):
            run(["x" * 4_097])
        with self.assertRaises(ValueError):
            run([f"f{i}" for i in range(5_001)])
        # None / list / tuple are fine.
        self.assertIn("findings", run(None))
        self.assertIn("findings", run(["README.md"]))
        self.assertIn("findings", run(("README.md",)))

    def test_project_summary_validates_too(self):
        with self.assertRaises(ValueError):
            PyprojectLintTool().execute(mode="project_summary")
        with self.assertRaises(ValueError):
            PyprojectLintTool().execute(
                mode="project_summary", pyproject=1
            )

    def test_deep_nesting_is_a_finding_not_a_crash(self):
        """Regression: ~500-level-deep TOML nesting used to raise
        RecursionError out of execute (tomllib's recursive-descent
        parser overflows the interpreter recursion limit and the
        except clause only caught TOMLDecodeError)."""
        deep_arrays = "a = " + "[" * 2_000 + "]" * 2_000
        result = run_lint(deep_arrays)
        self.assertEqual(codes(result), ["toml_parse_error"])
        self.assertIn("too deep", result["findings"][0]["message"])
        self.assertEqual(result["counts"]["errors"], 1)
        deep_tables = "a = " + "{x = " * 1_500 + "1" + "}" * 1_500
        result = run_lint(deep_tables)
        self.assertEqual(codes(result), ["toml_parse_error"])
        # The summary mode degrades to the none layout, no raise.
        result = run_summary(deep_arrays)
        self.assertEqual(result["layout"], "none")
        self.assertIn("too deep", result["note"])
        # Shallow nesting still parses normally.
        result = run_lint("a = [[1], [2]]\n")
        self.assertEqual(
            codes(result), ["build_system_missing", "missing_project_table"]
        )

    def test_cap_fields_are_live_configuration(self):
        """Regression: max_lines & co were documented Attributes but
        not model fields — setting them raised (pydantic) and the
        validation silently used the module constants only."""
        tool = PyprojectLintTool()
        self.assertEqual(tool.max_lines, 10_000)
        self.assertEqual(tool.max_line_chars, 10_000)
        self.assertEqual(tool.max_text_chars, 4_000_000)
        self.assertEqual(tool.max_files, 5_000)
        self.assertEqual(tool.max_file_entry_chars, 4_096)
        tool = PyprojectLintTool(max_lines=5, max_line_chars=50)
        # 6 lines / 51 chars exceed the configured caps...
        with self.assertRaises(ValueError):
            tool.execute(mode="lint", pyproject="x\n" * 6)
        with self.assertRaises(ValueError):
            tool.execute(mode="lint", pyproject="y" * 51)
        # ...while 5 x 50 chars passes input validation.
        result = tool.execute(mode="lint", pyproject="z" * 50 + "\n" * 4)
        self.assertIn("findings", result)
        tool = PyprojectLintTool(max_files=2, max_file_entry_chars=8)
        with self.assertRaises(ValueError):
            tool.execute(
                mode="lint", pyproject="[project]\n",
                available_files=["a", "b", "c"],
            )
        with self.assertRaises(ValueError):
            tool.execute(
                mode="lint", pyproject="[project]\n",
                available_files=["abcdefghi"],
            )
        result = tool.execute(
            mode="lint", pyproject="[project]\n",
            available_files=["a", "b"],
        )
        self.assertIn("findings", result)
        with self.assertRaises(ValueError):
            PyprojectLintTool(max_lines=0)  # caps must be >= 1

    def test_validation_errors_echo_is_bounded(self):
        """Regression: malformed-parameter errors echoed the whole
        value back via {value!r} (potentially megabytes / secrets)."""
        huge = ["x" * 500 for _ in range(500)]
        with self.assertRaises(ValueError) as ctx:
            PyprojectLintTool().execute(
                mode="lint", pyproject=huge
            )
        self.assertLess(len(str(ctx.exception)), 400)
        self.assertIn("…", str(ctx.exception))


# ------------------------------------------------------------------ #
# Differential vs packaging (when importable)
# ------------------------------------------------------------------ #

try:
    from packaging.version import InvalidVersion, Version
    from packaging.specifiers import InvalidSpecifier, SpecifierSet
    from packaging.requirements import InvalidRequirement, Requirement

    _PACKAGING = True
except ImportError:  # pragma: no cover - optional dependency
    _PACKAGING = False


@unittest.skipUnless(_PACKAGING, "packaging is not installed")
class PackagingDifferential(unittest.TestCase):
    """Grammar agreement with packaging 23.x over seeded strings."""

    @staticmethod
    def _version_seeds():
        rng = random.Random(2523)
        epochs = ["", "1!", "2!"]
        releases = [
            "0", "1", "3", "3.10", "1.0", "2.2.1", "1.0.0",
            "2024.10.21", "1.0.0.0.0", "0.0.19",
        ]
        pres = [
            "", "a1", "b2", "rc3", ".alpha1", "-beta2", "_preview3",
            "pre.4", "c5", "rc", "a", "post", "dev", "-r1",
        ]
        posts = ["", ".post1", "-post", "post2", "rev3", "-4", ".0"]
        devs = ["", ".dev1", "dev", "-dev.2", ".dev"]
        local = ["", "+local", "+local.1", "+LOCAL_2", "+a-b_c", "+5"]
        seeds = set()
        for _ in range(400):
            seeds.add(
                rng.choice(epochs) + rng.choice(releases)
                + rng.choice(pres) + rng.choice(posts)
                + rng.choice(devs) + rng.choice(local)
            )
        seeds.update(
            [
                "next", "1..2", "1.0-", "1.0.0!", "v", "1!", ".1", "1.",
                "1.0+", "1.0+a b", "1.0.0-", "x1", "1.a", "1.0.a",
                "1.0.0rc", "1.0.0rc.1?", "", "  ", "1.0 ", " 1.0",
                "0.0.19", "v0.3", "1!1.0-1", "!1.0",
            ]
        )
        return sorted(seeds)

    def test_version_differential(self):
        """packaging.Version accepts == _parse_version parses."""
        disagreements = []
        for seed in self._version_seeds():
            try:
                Version(seed)
                expected = True
            except InvalidVersion:
                expected = False
            from agentuniverse.agent.action.tool.common_tool \
                .pyproject_lint_tool import _parse_version
            actual = _parse_version(seed) is not None
            if actual != expected:
                disagreements.append((seed, expected, actual))
        self.assertEqual(
            disagreements, [], f"grammar diverged: {disagreements[:10]}"
        )

    @staticmethod
    def _specifier_seeds():
        rng = random.Random(2524)
        ops = ["==", "!=", "<=", ">=", "~=", "<", ">", "==="]
        tokens = [
            "3.10", "3", "4.0", "3.10.1", "2", "1.0+local", "3.10.*",
            "v3.10", "3.*", "anything", "1.2.*", "1!2.0",
        ]
        seeds = set()
        for _ in range(300):
            count = rng.randint(1, 3)
            clauses = [
                rng.choice(ops) + rng.choice(tokens)
                for _ in range(count)
            ]
            seeds.add(rng.choice([",", ", "]).join(clauses))
        seeds.update(
            [
                "", "3.10", ">=3.10,", ">=3.10, ", ">= 3.10", " ",
                ">=3.10,,", ",,", "~=3", "~=1", ">=",
                "==3.10.*", "!=3.9.*", ">=3.10.*", "<=1.0+local",
                "===anything", "===1.*", "==1.0+local", "!=1.0+local",
            ]
        )
        return sorted(seeds)

    def test_specifier_differential(self):
        """SpecifierSet accepts == _parse_specifier accepts."""
        from agentuniverse.agent.action.tool.common_tool \
            .pyproject_lint_tool import _parse_specifier
        disagreements = []
        for seed in self._specifier_seeds():
            try:
                SpecifierSet(seed)
                expected = True
            except InvalidSpecifier:
                expected = False
            _clauses, error = _parse_specifier(seed)
            if (error is None) != expected:
                disagreements.append((seed, expected, error))
        # The single allowed divergence: packaging quirk-accepts a
        # bare '===' as arbitrary equality against the EMPTY string
        # (any real comparison raises InvalidVersion); per PEP 440
        # the token must be non-empty, so the tool rejects it.
        quirk = [d for d in disagreements if d[0].strip() == "==="]
        other = [d for d in disagreements if d not in quirk]
        self.assertEqual(other, [], f"grammar diverged: {other[:10]}")

    @staticmethod
    def _requirement_seeds():
        rng = random.Random(2525)
        names = [
            "foo", "Foo_bar", "baz.qux", "a1", "x-y", "x_y", "zope",
            "old-setuptools",
        ]
        specs = [
            "", ">=1.0", ">=1.0,<2", " (>=1.0, <2)", "()", "( >=1.0 )",
            "==1.2.*", "!=3.9.*", "~=5.0", "~=1.0rc1", "===whatever!!",
            ">=1.0,", "(>=1.0,)", "==1.0+local", "==1!2.0", ">v1.0",
            ">=1.*", "==abc", "<1.0+loc", "~=1.0.*", "~=1", ">=1.0,,<2",
            "==1.0+local,<2", "===", ">= ,<2", "=== 1.0",
        ]
        extras = ["", "[]", "[security]", "[ e1 , e2 ]", "[e1,]"]
        markers = ["", " ; python_version < '3.11'", " ; extra == 'x'"]
        seeds = set()
        for _ in range(400):
            seeds.add(
                rng.choice(names) + rng.choice(extras)
                + rng.choice(specs) + rng.choice(markers)
            )
        seeds.update(
            [
                "direct @ https://example.com/x.whl",
                "with-marker @ https://example.com/x.whl ; os_name"
                " == 'nt'",
                "foo (>=1.0); python_version<'4'", "foo(>=1.0",
                "foo>=1.0)", "-foo", "foo-", "3foo", "foo bar",
                "no name here ==", ">=1.0", "",
            ]
        )
        return sorted(seeds)

    def test_requirement_differential(self):
        """Requirement accepts == _parse_requirement_string accepts.

        Excludes only the documented bare-=== quirk (packaging
        parses 'foo===' as arbitrary equality against the EMPTY
        string — unusable; asserted separately below).
        """
        from agentuniverse.agent.action.tool.common_tool \
            .pyproject_lint_tool import _parse_requirement_string
        disagreements = []
        for seed in self._requirement_seeds():
            try:
                Requirement(seed)
                expected = True
            except InvalidRequirement:
                expected = False
            _name, error = _parse_requirement_string(seed)
            if (error is None) != expected:
                disagreements.append((seed, expected, error))
        quirk = [
            d for d in disagreements
            if d[0].partition(";")[0].strip().endswith("===")
        ]
        other = [d for d in disagreements if d not in quirk]
        self.assertEqual(other, [], f"grammar diverged: {other[:10]}")

    def test_bare_arbitrary_equality_quirk(self):
        """The one deliberate divergence, pinned: packaging accepts
        a bare '===' / 'foo ===' (empty arbitrary-equality token —
        str(Specifier) round-trips but any comparison raises
        InvalidVersion); PEP 440 requires a token, so we reject."""
        from agentuniverse.agent.action.tool.common_tool \
            .pyproject_lint_tool import _parse_requirement_string
        self.assertIsNotNone(
            _parse_requirement_string("foo ===")[1]
        )
        self.assertIsNotNone(
            _parse_requirement_string("foo === ")[1]
        )


# ------------------------------------------------------------------ #
# Registration sanity
# ------------------------------------------------------------------ #

class Registration(unittest.TestCase):
    """Package-level and direct imports are the same class."""

    def test_same_class(self):
        self.assertIs(PyprojectLintTool, DirectPyprojectLintTool)

    def test_tool_metadata(self):
        tool = PyprojectLintTool()
        self.assertEqual(tool.name, "pyproject_lint_tool")
        self.assertIn("PEP 621", tool.description)


if __name__ == "__main__":
    unittest.main()
