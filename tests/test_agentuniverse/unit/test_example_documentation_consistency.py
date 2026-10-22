from pathlib import Path

import tomli

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def read_repository_file(relative_path: str) -> str:
    return (REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8")


def test_canonical_sample_and_install_guides_match_package_version():
    root_pyproject = tomli.loads(read_repository_file("pyproject.toml"))
    sample_pyproject = tomli.loads(read_repository_file("examples/sample_standard_app/pyproject.toml"))
    package_version = root_pyproject["tool"]["poetry"]["version"]

    assert sample_pyproject["tool"]["poetry"]["dependencies"]["agentUniverse"] == (f"~{package_version}")
    for guide_path in (
        "docs/guidebook/en/Get_Start/0.Installation_and_Initialization.md",
        "docs/guidebook/zh/开始使用/0.安装及创建标准工程.md",
    ):
        assert f'agentUniverse = "^{package_version}"' in read_repository_file(guide_path)


def test_canonical_sample_image_starts_an_existing_bootstrap_application():
    start_script = read_repository_file("examples/sample_standard_app/image_build/shell/start.sh")

    assert "bootstrap/platform" not in start_script
    assert "cd ./bootstrap/intelligence" in start_script
    assert "python3 -u server_application.py" in start_script
    assert (REPOSITORY_ROOT / "examples/sample_standard_app/bootstrap/intelligence/server_application.py").is_file()


def test_product_platform_guides_use_the_difizen_example_consistently():
    guide_paths = (
        "docs/guidebook/en/How-to/Guide to Visual Agentic Workflow Platform/Product_Platform_Quick_Start.md",
        "docs/guidebook/zh/How-to/画布式研发平台使用/画布式研发平台快速开始.md",
        "docs/guidebook/zh/设计理念/简介.md",
    )

    for guide_path in guide_paths:
        guide = read_repository_file(guide_path)
        assert "examples/sample_standard_app/bootstrap/platform" not in guide
        assert "sample_standard_app.platform.difizen.product" not in guide
        assert "difizen_app" in guide

    assert (REPOSITORY_ROOT / "examples/sample_apps/difizen_app/bootstrap/platform/product_application.py").is_file()
