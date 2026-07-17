# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for cloud reader refactoring (PR2).

These tests are designed to run without the full agentuniverse
framework (no tomli / langchain_core required).  They validate:
- CloudDocReader platform detection logic (mocked base classes)
- FeishuReader / YuqueReader / ConfluenceReader / NotionReader /
  GoogleDocsReader exception normalization (mocked base classes)
- ReaderManager URL_PATTERN_MAP and get_url_default_reader
- YAML registration correctness (module paths, class names)
- cloud_file_reader directory removal
- Backward-compat alias PublicFeishuReader

Strategy: We use importlib.util to load each reader module directly
from its file path, bypassing the cloud/__init__.py which would
trigger heavy imports (atlassian, notion-client, etc.).  Parent
packages are stubbed with __path__ so submodule resolution works.
"""

import importlib
import importlib.util
import os
import sys
import types
import unittest
from unittest.mock import patch, MagicMock

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "..", "..", ".."
))
_READER_DIR = os.path.join(
    _PROJECT_ROOT, "agentuniverse", "agent", "action", "knowledge", "reader"
)
_CLOUD_DIR = os.path.join(_READER_DIR, "cloud")
_CFR_DIR = os.path.join(_READER_DIR, "cloud_file_reader")

# ---------------------------------------------------------------------------
# Stub infrastructure
# ---------------------------------------------------------------------------

def _make_stub_reader():
    """Create a stub Reader base class."""
    class StubReader:
        component_type = "READER"
        name = None
        description = None
        def load_data(self, *args, **kwargs):
            return self._load_data(*args, **kwargs)
        def _load_data(self, *args, **kwargs):
            raise NotImplementedError
    return StubReader


def _make_stub_document():
    """Create a stub Document class."""
    class StubDocument:
        def __init__(self, text="", metadata=None):
            self.text = text
            self.metadata = metadata or {}
    return StubDocument


def _setup_stubs():
    """Set up lightweight stubs for heavy agentuniverse dependencies.

    We stub intermediate packages with __path__ so that Python can
    resolve submodule imports.  Leaf modules that contain actual code
    we need (reader.reader, store.document, etc.) get stub classes.
    """
    # Package stubs with __path__ for submodule discovery
    pkg_dirs = {
        "agentuniverse": os.path.join(_PROJECT_ROOT, "agentuniverse"),
        "agentuniverse.agent": os.path.join(_PROJECT_ROOT, "agentuniverse", "agent"),
        "agentuniverse.agent.action": os.path.join(_PROJECT_ROOT, "agentuniverse", "agent", "action"),
        "agentuniverse.agent.action.knowledge": os.path.join(_PROJECT_ROOT, "agentuniverse", "agent", "action", "knowledge"),
        "agentuniverse.agent.action.knowledge.reader": _READER_DIR,
        "agentuniverse.agent.action.knowledge.reader.cloud": _CLOUD_DIR,
        "agentuniverse.agent.action.knowledge.store": os.path.join(_PROJECT_ROOT, "agentuniverse", "agent", "action", "knowledge", "store"),
        "agentuniverse.base": os.path.join(_PROJECT_ROOT, "agentuniverse", "base"),
        "agentuniverse.base.annotation": os.path.join(_PROJECT_ROOT, "agentuniverse", "base", "annotation"),
        "agentuniverse.base.component": os.path.join(_PROJECT_ROOT, "agentuniverse", "base", "component"),
        "agentuniverse.base.config": os.path.join(_PROJECT_ROOT, "agentuniverse", "base", "config"),
        "agentuniverse.base.config.component_configer": os.path.join(_PROJECT_ROOT, "agentuniverse", "base", "config", "component_configer"),
        "agentuniverse.base.config.application_configer": os.path.join(_PROJECT_ROOT, "agentuniverse", "base", "config", "application_configer"),
        "agentuniverse.database": os.path.join(_PROJECT_ROOT, "agentuniverse", "database"),
    }
    for mod_path, pkg_dir in pkg_dirs.items():
        if mod_path not in sys.modules:
            mod = types.ModuleType(mod_path)
            mod.__path__ = [pkg_dir]
            mod.__package__ = mod_path
            sys.modules[mod_path] = mod

    # Leaf stubs with actual classes
    reader_mod = types.ModuleType("agentuniverse.agent.action.knowledge.reader.reader")
    reader_mod.Reader = _make_stub_reader()
    sys.modules["agentuniverse.agent.action.knowledge.reader.reader"] = reader_mod

    doc_mod = types.ModuleType("agentuniverse.agent.action.knowledge.store.document")
    doc_mod.Document = _make_stub_document()
    sys.modules["agentuniverse.agent.action.knowledge.store.document"] = doc_mod

    singleton_mod = types.ModuleType("agentuniverse.base.annotation.singleton")
    singleton_mod.singleton = lambda cls: cls
    sys.modules["agentuniverse.base.annotation.singleton"] = singleton_mod

    comp_enum_mod = types.ModuleType("agentuniverse.base.component.component_enum")
    class StubComponentEnum:
        READER = "READER"
    comp_enum_mod.ComponentEnum = StubComponentEnum
    sys.modules["agentuniverse.base.component.component_enum"] = comp_enum_mod

    comp_base_mod = types.ModuleType("agentuniverse.base.component.component_base")
    comp_base_mod.ComponentBase = object
    comp_base_mod.ComponentEnum = StubComponentEnum
    sys.modules["agentuniverse.base.component.component_base"] = comp_base_mod

    comp_mgr_mod = types.ModuleType("agentuniverse.base.component.component_manager_base")

    class StubComponentManagerBase:
        def __init_subclass__(cls, **kwargs): pass
        def __init__(self, *args, **kwargs): pass
        def __class_getitem__(cls, item):
            return cls
        def get_instance_obj(self, *args, **kwargs):
            return None

    comp_mgr_mod.ComponentManagerBase = StubComponentManagerBase
    comp_mgr_mod.ComponentTypeVar = object
    sys.modules["agentuniverse.base.component.component_manager_base"] = comp_mgr_mod

    configer_mod = types.ModuleType("agentuniverse.base.config.configer")
    sys.modules["agentuniverse.base.config.configer"] = configer_mod

    comp_cfg_mod = types.ModuleType("agentuniverse.base.config.component_configer.component_configer")
    comp_cfg_mod.ComponentConfiger = object
    sys.modules["agentuniverse.base.config.component_configer.component_configer"] = comp_cfg_mod

    app_cfg_mod = types.ModuleType("agentuniverse.base.config.application_configer.app_configer")
    app_cfg_mod.AppConfiger = object
    sys.modules["agentuniverse.base.config.application_configer.app_configer"] = app_cfg_mod

    app_cfg_mgr_mod = types.ModuleType("agentuniverse.base.config.application_configer.application_config_manager")
    app_cfg_mgr_mod.ApplicationConfigManager = object
    sys.modules["agentuniverse.base.config.application_configer.application_config_manager"] = app_cfg_mgr_mod

    # Stub cloud __init__ to avoid importing all readers at once
    cloud_init_mod = types.ModuleType("agentuniverse.agent.action.knowledge.reader.cloud")
    cloud_init_mod.__path__ = [_CLOUD_DIR]
    cloud_init_mod.__package__ = "agentuniverse.agent.action.knowledge.reader.cloud"
    sys.modules["agentuniverse.agent.action.knowledge.reader.cloud"] = cloud_init_mod

    # Stub sub-packages that are imported but don't need real code
    for sub in [
        "agentuniverse.agent.action.knowledge.reader.file",
        "agentuniverse.agent.action.knowledge.reader.image",
        "agentuniverse.agent.action.knowledge.reader.web",
    ]:
        if sub not in sys.modules:
            m = types.ModuleType(sub)
            m.__path__ = []
            sys.modules[sub] = m

    # Stub heavy external dependencies so reader modules can load
    # pydantic
    pydantic_mod = types.ModuleType("pydantic")
    class StubBaseModel:
        def __init_subclass__(cls, **kwargs): pass
        model_config = {}
    pydantic_mod.BaseModel = StubBaseModel
    pydantic_mod.ConfigDict = lambda **kwargs: kwargs
    pydantic_mod.Field = lambda *a, **kw: None
    sys.modules["pydantic"] = pydantic_mod

    # requests
    requests_mod = types.ModuleType("requests")
    class StubSession:
        def __init__(self): pass
        def get(self, *a, **kw): raise NotImplementedError
        def post(self, *a, **kw): raise NotImplementedError
    requests_mod.Session = StubSession
    requests_mod.adapters = types.ModuleType("requests.adapters")
    requests_mod.adapters.HTTPAdapter = type("HTTPAdapter", (), {})
    requests_mod.adapters.Retry = type("Retry", (), {})
    sys.modules["requests"] = requests_mod
    sys.modules["requests.adapters"] = requests_mod.adapters

    # requests.exceptions (needed by old yuque_reader)
    requests_exc_mod = types.ModuleType("requests.exceptions")
    class StubRequestException(Exception):
        pass
    requests_exc_mod.RequestException = StubRequestException
    requests_mod.exceptions = requests_exc_mod
    sys.modules["requests.exceptions"] = requests_exc_mod

    # selenium stubs (needed by old feishu_reader)
    selenium_mod = types.ModuleType("selenium")
    selenium_webdriver_mod = types.ModuleType("selenium.webdriver")
    selenium_chrome_mod = types.ModuleType("selenium.webdriver.chrome")
    selenium_chrome_options_mod = types.ModuleType("selenium.webdriver.chrome.options")
    class StubOptions:
        def add_argument(self, *a): pass
    selenium_chrome_options_mod.Options = StubOptions
    class StubWebDriver:
        def __init__(self, *a, **kw): pass
    selenium_webdriver_mod.Chrome = StubWebDriver
    selenium_mod.webdriver = selenium_webdriver_mod
    for m, mod_obj in [
        ("selenium", selenium_mod),
        ("selenium.webdriver", selenium_webdriver_mod),
        ("selenium.webdriver.chrome", selenium_chrome_mod),
        ("selenium.webdriver.chrome.options", selenium_chrome_options_mod),
    ]:
        sys.modules[m] = mod_obj

    # bs4 stub (needed by old feishu_reader and yuque_reader)
    bs4_mod = types.ModuleType("bs4")
    class StubBeautifulSoup:
        def __init__(self, *a, **kw): pass
    bs4_mod.BeautifulSoup = StubBeautifulSoup
    sys.modules["bs4"] = bs4_mod

    # atlassian
    atlassian_mod = types.ModuleType("atlassian")
    atlassian_mod.Confluence = type("Confluence", (), {})
    sys.modules["atlassian"] = atlassian_mod

    # notion_client
    notion_client_mod = types.ModuleType("notion_client")
    notion_client_mod.Client = type("Client", (), {})
    sys.modules["notion_client"] = notion_client_mod

    # google.oauth2 and googleapiclient
    google_mod = types.ModuleType("google")
    google_oauth2_mod = types.ModuleType("google.oauth2")
    google_oauth2_svc_mod = types.ModuleType("google.oauth2.service_account")
    google_oauth2_svc_mod.Credentials = type("Credentials", (), {"from_service_account_file": classmethod(lambda cls, *a, **kw: None)})
    googleapiclient_mod = types.ModuleType("googleapiclient")
    googleapiclient_disc_mod = types.ModuleType("googleapiclient.discovery")
    googleapiclient_disc_mod.build = lambda *a, **kw: None
    for m, mod_obj in [
        ("google", google_mod),
        ("google.oauth2", google_oauth2_mod),
        ("google.oauth2.service_account", google_oauth2_svc_mod),
        ("googleapiclient", googleapiclient_mod),
        ("googleapiclient.discovery", googleapiclient_disc_mod),
    ]:
        sys.modules[m] = mod_obj


def _load_module_from_file(module_name, file_path):
    """Load a Python module directly from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Setup: load all modules under test
# ---------------------------------------------------------------------------
_setup_stubs()

# Load reader_errors first (no heavy deps)
_errors_mod = _load_module_from_file(
    "agentuniverse.agent.action.knowledge.reader.reader_errors",
    os.path.join(_READER_DIR, "reader_errors.py"),
)
ReaderError = _errors_mod.ReaderError
ReaderLoadError = _errors_mod.ReaderLoadError
ReaderDependencyError = _errors_mod.ReaderDependencyError
ReaderParseError = _errors_mod.ReaderParseError
ReaderConfigError = _errors_mod.ReaderConfigError

# Load cloud readers individually (bypassing cloud/__init__.py)
_cloud_doc_mod = _load_module_from_file(
    "agentuniverse.agent.action.knowledge.reader.cloud.cloud_doc_reader",
    os.path.join(_CLOUD_DIR, "cloud_doc_reader.py"),
)
CloudDocReader = _cloud_doc_mod.CloudDocReader
_platform_map = _cloud_doc_mod._platform_map
register_platform = _cloud_doc_mod.register_platform
unregister_platform = _cloud_doc_mod.unregister_platform
get_platform_map = _cloud_doc_mod.get_platform_map

_feishu_mod = _load_module_from_file(
    "agentuniverse.agent.action.knowledge.reader.cloud.feishu_reader",
    os.path.join(_CLOUD_DIR, "feishu_reader.py"),
)
FeishuReader = _feishu_mod.FeishuReader
PublicFeishuReader = _feishu_mod.PublicFeishuReader

_yuque_mod = _load_module_from_file(
    "agentuniverse.agent.action.knowledge.reader.cloud.yuque_reader",
    os.path.join(_CLOUD_DIR, "yuque_reader.py"),
)
YuqueReader = _yuque_mod.YuqueReader

_confluence_mod = _load_module_from_file(
    "agentuniverse.agent.action.knowledge.reader.cloud.confluence_reader",
    os.path.join(_CLOUD_DIR, "confluence_reader.py"),
)
ConfluenceReader = _confluence_mod.ConfluenceReader

_notion_mod = _load_module_from_file(
    "agentuniverse.agent.action.knowledge.reader.cloud.notion_reader",
    os.path.join(_CLOUD_DIR, "notion_reader.py"),
)
NotionReader = _notion_mod.NotionReader

_gdocs_mod = _load_module_from_file(
    "agentuniverse.agent.action.knowledge.reader.cloud.google_docs_reader",
    os.path.join(_CLOUD_DIR, "google_docs_reader.py"),
)
GoogleDocsReader = _gdocs_mod.GoogleDocsReader


# ---------------------------------------------------------------------------
# CloudDocReader tests
# ---------------------------------------------------------------------------

class TestCloudDocReaderPlatformDetection(unittest.TestCase):
    """Test CloudDocReader._detect_platform."""

    def test_detect_feishu(self):
        reader = CloudDocReader()
        self.assertEqual(
            reader._detect_platform("https://www.feishu.cn/docx/abc123"),
            "default_feishu_reader",
        )

    def test_detect_yuque(self):
        reader = CloudDocReader()
        self.assertEqual(
            reader._detect_platform("https://www.yuque.com/antx/ld6v0l/glg40g"),
            "default_yuque_reader",
        )

    def test_detect_notion(self):
        reader = CloudDocReader()
        self.assertEqual(
            reader._detect_platform("https://www.notion.so/Workspace/Page-abc123"),
            "default_notion_reader",
        )

    def test_detect_confluence(self):
        reader = CloudDocReader()
        self.assertEqual(
            reader._detect_platform("https://confluence.example.com/display/ENG/Page"),
            "default_confluence_reader",
        )

    def test_detect_google_docs(self):
        reader = CloudDocReader()
        self.assertEqual(
            reader._detect_platform("https://docs.google.com/document/d/1abc/edit"),
            "default_google_docs_reader",
        )

    def test_detect_unknown_returns_none(self):
        reader = CloudDocReader()
        self.assertIsNone(reader._detect_platform("https://www.example.com/page"))

    def test_detect_empty_url_returns_none(self):
        reader = CloudDocReader()
        self.assertIsNone(reader._detect_platform(""))

    def test_detect_invalid_url_returns_none(self):
        reader = CloudDocReader()
        self.assertIsNone(reader._detect_platform("not-a-url"))


class TestCloudDocReaderLoadData(unittest.TestCase):
    """Test CloudDocReader._load_data error paths."""

    def test_empty_url_raises_reader_load_error(self):
        reader = CloudDocReader()
        with self.assertRaises(ReaderLoadError):
            reader._load_data("")

    def test_unsupported_url_raises_reader_load_error(self):
        reader = CloudDocReader()
        with self.assertRaises(ReaderLoadError):
            reader._load_data("https://www.example.com/page")


class TestPlatformMapAPI(unittest.TestCase):
    """Test register_platform / unregister_platform / get_platform_map."""

    def test_get_platform_map_returns_copy(self):
        m = get_platform_map()
        self.assertIsInstance(m, dict)
        self.assertIn("feishu.cn", m)

    def test_register_and_unregister(self):
        original = get_platform_map()
        register_platform("example.com", "custom_reader")
        self.assertEqual(get_platform_map()["example.com"], "custom_reader")
        unregister_platform("example.com")
        self.assertNotIn("example.com", get_platform_map())
        # Restore
        _cloud_doc_mod._platform_map = original


# ---------------------------------------------------------------------------
# FeishuReader tests
# ---------------------------------------------------------------------------

class TestFeishuReaderExceptions(unittest.TestCase):

    def test_empty_url_raises_reader_load_error(self):
        reader = FeishuReader()
        with self.assertRaises(ReaderLoadError):
            reader._load_data("")

    def test_missing_selenium_raises_reader_dependency_error(self):
        reader = FeishuReader()
        with patch.dict("sys.modules", {"selenium": None}):
            with self.assertRaises(ReaderDependencyError) as ctx:
                reader._get_driver()
            self.assertIn("selenium", str(ctx.exception))

    def test_backward_compat_alias(self):
        self.assertIs(PublicFeishuReader, FeishuReader)


# ---------------------------------------------------------------------------
# YuqueReader tests
# ---------------------------------------------------------------------------

class TestYuqueReaderExceptions(unittest.TestCase):

    def test_empty_url_raises_reader_load_error(self):
        # YuqueReader.__init__ needs requests — mock it
        mock_requests = MagicMock()
        mock_session = MagicMock()
        mock_requests.Session.return_value = mock_session
        mock_requests.adapters = MagicMock()
        mock_requests.adapters.HTTPAdapter = MagicMock
        mock_requests.adapters.Retry = MagicMock
        with patch.dict("sys.modules", {
            "requests": mock_requests,
            "requests.adapters": mock_requests.adapters,
        }):
            _yuque_mod2 = _load_module_from_file(
                "agentuniverse.agent.action.knowledge.reader.cloud.yuque_reader_v2",
                os.path.join(_CLOUD_DIR, "yuque_reader.py"),
            )
            reader = _yuque_mod2.YuqueReader()
            with self.assertRaises(ReaderLoadError):
                reader._load_data("")


# ---------------------------------------------------------------------------
# ConfluenceReader tests
# ---------------------------------------------------------------------------

class TestConfluenceReaderExceptions(unittest.TestCase):

    def test_empty_page_id_raises_reader_load_error(self):
        reader = ConfluenceReader()
        with self.assertRaises(ReaderLoadError):
            reader._load_data("")

    def test_missing_credentials_raises_reader_config_error(self):
        reader = ConfluenceReader()
        with self.assertRaises(ReaderConfigError) as ctx:
            reader._resolve_cred(None)
        self.assertIn("CONFLUENCE", str(ctx.exception))

    def test_missing_atlassian_raises_reader_dependency_error(self):
        reader = ConfluenceReader()
        with patch.dict("sys.modules", {"atlassian": None}):
            with self.assertRaises(ReaderDependencyError) as ctx:
                reader._load_data("12345", ext_info={
                    "site_url": "https://wiki.example.com",
                    "username": "user",
                    "token": "tok",
                })
            self.assertIn("atlassian-python-api", str(ctx.exception))


# ---------------------------------------------------------------------------
# NotionReader tests
# ---------------------------------------------------------------------------

class TestNotionReaderExceptions(unittest.TestCase):

    def test_empty_id_raises_reader_load_error(self):
        reader = NotionReader()
        with self.assertRaises(ReaderLoadError):
            reader._load_data("")

    def test_missing_token_raises_reader_config_error(self):
        reader = NotionReader()
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ReaderConfigError) as ctx:
                reader._load_data("some-id")
            self.assertIn("NOTION_TOKEN", str(ctx.exception))


# ---------------------------------------------------------------------------
# GoogleDocsReader tests
# ---------------------------------------------------------------------------

class TestGoogleDocsReaderExceptions(unittest.TestCase):

    def test_empty_doc_id_raises_reader_load_error(self):
        reader = GoogleDocsReader()
        with self.assertRaises(ReaderLoadError):
            reader._load_data("")

    def test_missing_sa_path_raises_reader_config_error(self):
        reader = GoogleDocsReader()
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ReaderConfigError) as ctx:
                reader._build_drive_service(None)
            self.assertIn("GOOGLE_SERVICE_ACCOUNT_JSON", str(ctx.exception))


# ---------------------------------------------------------------------------
# ReaderManager URL routing tests
# ---------------------------------------------------------------------------

class TestReaderManagerURLPatternMap(unittest.TestCase):
    """Test ReaderManager.URL_PATTERN_MAP structure."""

    def _import_manager(self):
        """Import ReaderManager with stubs."""
        rm_mod = _load_module_from_file(
            "agentuniverse.agent.action.knowledge.reader.reader_manager_v2",
            os.path.join(_READER_DIR, "reader_manager.py"),
        )
        return rm_mod.ReaderManager

    def test_url_pattern_map_has_five_entries(self):
        ReaderManagerCls = self._import_manager()
        mgr = ReaderManagerCls()
        self.assertEqual(len(mgr.URL_PATTERN_MAP), 5)

    def test_url_pattern_map_keys(self):
        ReaderManagerCls = self._import_manager()
        mgr = ReaderManagerCls()
        expected_keys = {"feishu.cn", "yuque.com", "notion.so", "confluence", "docs.google.com"}
        self.assertEqual(set(mgr.URL_PATTERN_MAP.keys()), expected_keys)

    def test_get_url_default_reader_feishu(self):
        ReaderManagerCls = self._import_manager()
        mgr = ReaderManagerCls()
        with patch.object(mgr, "get_instance_obj", return_value=MagicMock()) as mock_get:
            result = mgr.get_url_default_reader("https://www.feishu.cn/docx/abc")
            mock_get.assert_called_once_with("default_feishu_reader")
            self.assertIsNotNone(result)

    def test_get_url_default_reader_unknown_returns_none(self):
        ReaderManagerCls = self._import_manager()
        mgr = ReaderManagerCls()
        result = mgr.get_url_default_reader("https://www.example.com/page")
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# YAML registration tests
# ---------------------------------------------------------------------------

class TestYAMLRegistration(unittest.TestCase):
    """Verify YAML files have correct module paths and class names."""

    def _read_yaml_value(self, yaml_path, key_path):
        """Read a value from a YAML file using simple text parsing.

        Avoids the ``pyyaml`` dependency by doing line-based matching.
        *key_path* is a dot-separated path, e.g. ``metadata.module``.
        """
        with open(yaml_path) as f:
            lines = f.readlines()
        keys = key_path.split(".")
        # Simple two-level YAML: look for "  <key>:" then "    <subkey>:"
        if len(keys) == 2:
            top_key, sub_key = keys
            in_top = False
            for line in lines:
                stripped = line.rstrip()
                if stripped.startswith(f"{top_key}:"):
                    in_top = True
                    continue
                if in_top:
                    if stripped.startswith(f"  {sub_key}:"):
                        # Extract value after colon
                        val = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                        return val
                    # If we hit another top-level key, stop
                    if stripped and not stripped.startswith((" ", "\t")):
                        break
        return None

    def test_feishu_yaml_module_path(self):
        val = self._read_yaml_value(
            os.path.join(_CLOUD_DIR, "feishu_reader.yaml"), "metadata.module"
        )
        self.assertEqual(
            val,
            "agentuniverse.agent.action.knowledge.reader.cloud.feishu_reader",
        )
        cls = self._read_yaml_value(
            os.path.join(_CLOUD_DIR, "feishu_reader.yaml"), "metadata.class"
        )
        self.assertEqual(cls, "FeishuReader")

    def test_yuque_yaml_module_path(self):
        val = self._read_yaml_value(
            os.path.join(_CLOUD_DIR, "yuque_reader.yaml"), "metadata.module"
        )
        self.assertEqual(
            val,
            "agentuniverse.agent.action.knowledge.reader.cloud.yuque_reader",
        )
        cls = self._read_yaml_value(
            os.path.join(_CLOUD_DIR, "yuque_reader.yaml"), "metadata.class"
        )
        self.assertEqual(cls, "YuqueReader")

    def test_cloud_doc_yaml_module_path(self):
        val = self._read_yaml_value(
            os.path.join(_CLOUD_DIR, "cloud_doc_reader.yaml"), "metadata.module"
        )
        self.assertEqual(
            val,
            "agentuniverse.agent.action.knowledge.reader.cloud.cloud_doc_reader",
        )
        cls = self._read_yaml_value(
            os.path.join(_CLOUD_DIR, "cloud_doc_reader.yaml"), "metadata.class"
        )
        self.assertEqual(cls, "CloudDocReader")

    def test_confluence_yaml_unchanged(self):
        val = self._read_yaml_value(
            os.path.join(_CLOUD_DIR, "confluence_reader.yaml"), "metadata.module"
        )
        self.assertEqual(
            val,
            "agentuniverse.agent.action.knowledge.reader.cloud.confluence_reader",
        )

    def test_notion_yaml_unchanged(self):
        val = self._read_yaml_value(
            os.path.join(_CLOUD_DIR, "notion_reader.yaml"), "metadata.module"
        )
        self.assertEqual(
            val,
            "agentuniverse.agent.action.knowledge.reader.cloud.notion_reader",
        )

    def test_google_docs_yaml_unchanged(self):
        val = self._read_yaml_value(
            os.path.join(_CLOUD_DIR, "google_docs_reader.yaml"), "metadata.module"
        )
        self.assertEqual(
            val,
            "agentuniverse.agent.action.knowledge.reader.cloud.google_docs_reader",
        )


# ---------------------------------------------------------------------------
# cloud_file_reader backward-compatibility tests
# ---------------------------------------------------------------------------

class TestCloudFileReaderBackwardCompat(unittest.TestCase):
    """Verify cloud_file_reader/ provides backward-compatible old
    implementations (restored verbatim from master)."""

    def test_cloud_file_reader_dir_exists(self):
        self.assertTrue(os.path.isdir(_CFR_DIR),
                        f"cloud_file_reader/ should exist for backward compat, "
                        f"not found at {_CFR_DIR}")

    def test_cloud_file_reader_has_old_modules(self):
        for fname in ["__init__.py", "feishu_reader.py", "yuque_reader.py"]:
            fpath = os.path.join(_CFR_DIR, fname)
            self.assertTrue(os.path.isfile(fpath),
                            f"Expected {fname} in cloud_file_reader/, "
                            f"not found at {fpath}")

    def test_old_feishu_reader_has_original_class(self):
        """The restored PublicFeishuReader is the ORIGINAL standalone
        class (not an alias to cloud.FeishuReader)."""
        cfr_feishu = os.path.join(_CFR_DIR, "feishu_reader.py")
        # Load the old module directly
        old_mod = _load_module_from_file("cfr_feishu_reader", cfr_feishu)
        OldClass = old_mod.PublicFeishuReader
        # It must NOT be the same class as cloud.FeishuReader
        self.assertIsNot(OldClass, FeishuReader,
                         "Old PublicFeishuReader must be a distinct class, "
                         "not an alias to cloud.FeishuReader")
        # It must have the original public load_data method
        self.assertTrue(hasattr(OldClass, "load_data"))
        # It must NOT inherit from Reader
        StubReader = sys.modules[
            "agentuniverse.agent.action.knowledge.reader.reader"
        ].Reader
        self.assertFalse(issubclass(OldClass, StubReader),
                         "Old PublicFeishuReader should NOT be a Reader subclass")

    def test_old_yuque_reader_has_original_class(self):
        """The restored YuqueReader is the ORIGINAL implementation
        (not the new cloud.YuqueReader)."""
        cfr_yuque = os.path.join(_CFR_DIR, "yuque_reader.py")
        old_mod = _load_module_from_file("cfr_yuque_reader", cfr_yuque)
        OldClass = old_mod.YuqueReader
        # It must NOT be the same class as cloud.YuqueReader
        self.assertIsNot(OldClass, YuqueReader,
                         "Old YuqueReader must be a distinct class, "
                         "not the new cloud.YuqueReader")

    def test_cloud_dir_exists(self):
        self.assertTrue(os.path.isdir(_CLOUD_DIR))

    def test_cloud_dir_has_all_readers(self):
        expected_files = [
            "__init__.py",
            "cloud_doc_reader.py",
            "cloud_doc_reader.yaml",
            "feishu_reader.py",
            "feishu_reader.yaml",
            "yuque_reader.py",
            "yuque_reader.yaml",
            "confluence_reader.py",
            "confluence_reader.yaml",
            "notion_reader.py",
            "notion_reader.yaml",
            "google_docs_reader.py",
            "google_docs_reader.yaml",
        ]
        for fname in expected_files:
            fpath = os.path.join(_CLOUD_DIR, fname)
            self.assertTrue(os.path.isfile(fpath),
                            f"Expected {fname} in cloud/, not found at {fpath}")


# ---------------------------------------------------------------------------
# Exception hierarchy integration tests
# ---------------------------------------------------------------------------

class TestCloudReaderExceptionHierarchy(unittest.TestCase):
    """Verify all cloud readers raise ReaderError subclasses."""

    def test_feishu_reader_load_error_is_reader_error(self):
        reader = FeishuReader()
        with self.assertRaises(ReaderError):
            reader._load_data("")

    def test_confluence_config_error_is_reader_error(self):
        reader = ConfluenceReader()
        with self.assertRaises(ReaderError):
            reader._resolve_cred(None)

    def test_notion_config_error_is_reader_error(self):
        reader = NotionReader()
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ReaderError):
                reader._load_data("some-id")

    def test_google_docs_config_error_is_reader_error(self):
        reader = GoogleDocsReader()
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ReaderError):
                reader._build_drive_service(None)


if __name__ == "__main__":
    unittest.main()