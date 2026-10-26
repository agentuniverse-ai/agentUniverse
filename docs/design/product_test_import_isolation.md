# Product test import isolation

Product utilities use `ruamel.yaml` to read and write configuration files. Install
the real dependency in the test environment (`python -m pip install ruamel.yaml`).
Tests must not insert placeholder YAML modules into `sys.modules` during collection:
doing so can replace an installed package before its first import and break later
workflow tests with `AttributeError: 'object' object has no attribute 'dump'`.

The regression in `test_agent_util.py` imports that test module in a fresh Python
process and round-trips YAML through the implementation used by the product YAML
utility. A fresh process keeps an earlier import of the real package from hiding
collection-time pollution.

From the repository root, run the affected files in both orders:

```bash
python -m pytest -q \
  tests/test_agentuniverse_product/unit/service/util/test_agent_util.py \
  tests/test_agentuniverse_product/unit/service/test_workflow_service.py
python -m pytest -q \
  tests/test_agentuniverse_product/unit/service/test_workflow_service.py \
  tests/test_agentuniverse_product/unit/service/util/test_agent_util.py
```

This addresses the YAML module pollution reported in issue #4401. Chroma client
registry isolation is a separate cause described in that issue.
