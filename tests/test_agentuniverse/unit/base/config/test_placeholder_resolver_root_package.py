from agentuniverse.base.config.configer import PlaceholderResolver


def test_root_package_placeholder_uses_latest_loaded_project():
    resolver = PlaceholderResolver()

    resolver.set_root_package_name("first_project")
    assert resolver.resolve("${ROOT_PACKAGE}.agent") == "first_project.agent"

    resolver.set_root_package_name("second_project")
    assert resolver.resolve("${ROOT_PACKAGE}.agent") == "second_project.agent"
