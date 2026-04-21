import unittest

from tourism_automation.cli.main import build_parser


class UnifiedCliTests(unittest.TestCase):
    def test_build_parser_registers_collectors(self):
        parser = build_parser()
        collector_action = next(action for action in parser._actions if action.dest == "collector")

        self.assertEqual(sorted(collector_action.choices.keys()), ["fliggy-home", "sycm"])


if __name__ == "__main__":
    unittest.main()
