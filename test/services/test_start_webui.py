import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts import start_webui


class TestStartWebUI(unittest.TestCase):
    def test_find_available_port_skips_occupied_ports(self):
        occupied = {("127.0.0.1", 8501), ("127.0.0.1", 8502)}

        def connect_ex(address):
            return 0 if address in occupied else 1

        self.assertEqual(
            start_webui.find_available_port(connect_ex=connect_ex),
            8503,
        )

    def test_build_streamlit_command_uses_single_headless_flag(self):
        cmd = start_webui.build_streamlit_command(
            root_dir=Path("/tmp/project"),
            port=8501,
            uv_path="uv",
            headless=True,
        )

        headless_args = [arg for arg in cmd if arg.startswith("--server.headless=")]
        self.assertEqual(headless_args, ["--server.headless=true"])

    def test_print_preflight_adds_project_root_to_import_path(self):
        root_path = str(start_webui.ROOT_DIR)
        original_path = list(sys.path)
        sys.path = [path for path in sys.path if path != root_path]
        with patch.object(start_webui, "_load_config", return_value={}):
            try:
                start_webui.print_preflight(start_webui.ROOT_DIR)
                updated_path = list(sys.path)
            finally:
                sys.path = original_path

        self.assertIn(root_path, updated_path)


if __name__ == "__main__":
    unittest.main()
