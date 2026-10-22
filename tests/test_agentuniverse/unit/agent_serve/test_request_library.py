import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from agentuniverse.agent_serve.web.dal import request_library


class RequestLibraryTest(unittest.TestCase):
    def test_constructor_without_configer_uses_default_database_settings(self):
        wrapper = MagicMock()
        wrapper.get_instance_code.return_value = "test.sqldb.__system_db__"
        wrapper_class = MagicMock(return_value=wrapper)

        with TemporaryDirectory() as directory, patch.object(
            request_library, "get_project_root_path", return_value=Path(directory)
        ), patch.object(request_library, "SQLDBWrapper", wrapper_class), patch.object(
            request_library, "SQLDBWrapperManager"
        ) as manager:
            library = request_library.RequestLibrary.__wrapped__(configer=None)
            expected_uri = f"sqlite:///{directory}/intelligence/db/agent_universe.db"

        self.assertEqual(library.update_interval, 5)
        self.assertEqual(library.request_table_name, request_library.REQUEST_TABLE_NAME)
        self.assertEqual(
            wrapper_class.call_args.kwargs["db_wrapper_configer"].db_uri,
            expected_uri,
        )
        manager.return_value.register.assert_called_once_with(
            "test.sqldb.__system_db__", wrapper
        )


if __name__ == "__main__":
    unittest.main()
