import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from webui import onboarding
from webui.runtime_check import build_preflight_report


class TestOnboarding(unittest.TestCase):
    def test_recommends_local_for_unknown_or_local_mode(self):
        self.assertEqual(onboarding.recommended_source_for_mode("local"), "local")
        self.assertEqual(onboarding.recommended_source_for_mode(""), "local")

    def test_recommends_pexels_for_online_mode(self):
        self.assertEqual(onboarding.recommended_source_for_mode("online"), "pexels")

    def test_uses_online_mode_for_existing_online_sources(self):
        self.assertEqual(onboarding.mode_for_video_source("pexels"), "online")
        self.assertEqual(onboarding.mode_for_video_source("pixabay"), "online")
        self.assertEqual(onboarding.mode_for_video_source("local"), "local")

    def test_applies_quick_start_source_only_when_mode_changes(self):
        self.assertEqual(
            onboarding.source_for_mode_change(None, "local"),
            "local",
        )
        self.assertEqual(
            onboarding.source_for_mode_change("local", "local"),
            None,
        )
        self.assertEqual(
            onboarding.source_for_mode_change("local", "online"),
            "pexels",
        )

    def test_preflight_defaults_to_local_materials(self):
        report = build_preflight_report(
            root_dir=Path(__file__).parent.parent.parent,
            config_data={"app": {}, "ui": {}},
            which=lambda name: None,
        )

        material_check = next(
            check for check in report.checks if check.key == "material_source"
        )
        self.assertEqual(material_check.status, "ok")
        self.assertIn("本地素材", material_check.message)


if __name__ == "__main__":
    unittest.main()
