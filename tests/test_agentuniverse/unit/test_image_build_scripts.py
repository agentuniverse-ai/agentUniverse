from pathlib import Path

REPOSITORY_ROOT = Path(__file__).parents[3]
INSTALL_SCRIPTS = (
    "examples/sample_standard_app/image_build/shell/install_python.sh",
    "examples/third_party_examples/apps/app_with_goole_search_tool/image_build/shell/install_python.sh",
)


def test_miniforge_installers_are_pinned_and_verified():
    for relative_path in INSTALL_SCRIPTS:
        script = (REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8")

        assert "set -euo pipefail" in script
        assert "--no-check-certificate" not in script
        assert 'MINIFORGE_VERSION="26.3.2-3"' in script
        assert (
            'MINIFORGE_SHA256="848194851a98903134187fbb4ab50efe87b003e0c0f808f97644b7524a62bf2c"'
            in script
        )
        assert "github.com/conda-forge/miniforge/releases/download/" in script

        verification = 'echo "${MINIFORGE_SHA256}  ${MINIFORGE_INSTALLER}" | sha256sum -c -'
        execution = '"./${MINIFORGE_INSTALLER}" -b -p /usr/local/etc/workspace/miniforge'
        assert verification in script
        assert execution in script
        assert script.index(verification) < script.index(execution)
