from pathlib import Path
import unittest

from packaging.tags import Tag

import tempfile

from scripts.build_test_site import dockerfile_modules, select_wheels


class SelectWheelsTests(unittest.TestCase):
    def test_highest_compatible_version_per_distribution(self):
        cp312 = {Tag('cp312', 'cp312', 'manylinux_2_17_x86_64'), Tag('py3', 'none', 'any')}
        wheels = [Path(n) for n in (
            'pytest-6.2.5-py3-none-any.whl', 'pytest-9.1.1-py3-none-any.whl', 'pytest-8.3.4-py3-none-any.whl',
            'pydantic_core-2.46.4-cp313-cp313-manylinux_2_17_x86_64.whl',
            'pydantic_core-2.46.4-cp312-cp312-manylinux_2_17_x86_64.whl',
            'SQLAlchemy-2.0.51-cp313-cp313-manylinux_2_17_x86_64.whl',
            'sqlalchemy-2.0.52-cp312-cp312-manylinux_2_17_x86_64.whl',
            'only313-1.0-cp313-cp313-manylinux_2_17_x86_64.whl')]
        chosen = [w.name for w in select_wheels(wheels, cp312)]
        self.assertEqual(chosen, ['pydantic_core-2.46.4-cp312-cp312-manylinux_2_17_x86_64.whl',
                                  'pytest-9.1.1-py3-none-any.whl',
                                  'sqlalchemy-2.0.52-cp312-cp312-manylinux_2_17_x86_64.whl'])


    def test_only_modules_copied_into_site_packages_are_taken_from_the_dockerfile(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / 'Dockerfile.sandbox').write_text(
                'FROM python:3.13-slim\n'
                'COPY imp.py /usr/local/lib/python3.13/site-packages/imp.py\n'
                'COPY telnetlib.py /usr/local/lib/python3.13/site-packages/telnetlib.py\n'
                'COPY wheels/ /wheels/\n')
            self.assertEqual([p.name for p in dockerfile_modules(d)], ['imp.py', 'telnetlib.py'])


if __name__ == '__main__':
    unittest.main()
