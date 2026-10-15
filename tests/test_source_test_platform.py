"""Invalid execution platforms must fail before creating files or containers."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.compare_source_snapshot import run_image


class SourceTestPlatformTests(unittest.TestCase):
    def test_invalid_platform_has_no_side_effects(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'results'
            for platform in (None, '', 'arm64', 'linux/386', 'linux/arm64 --privileged', []):
                with self.subTest(platform=platform), patch('subprocess.run') as run:
                    with self.assertRaises(ValueError):
                        run_image('sha256:' + 'a' * 64, output, platform=platform)
                    run.assert_not_called()
                    self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
