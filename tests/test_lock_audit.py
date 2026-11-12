"""A pin passes only on an exact digest match; everything else is named."""

import unittest

from zenithsync.lock_audit import (DIGEST_ABSENT, NOT_ON_INDEX, SATISFIED,
                                   SDIST, VERSION_ABSENT, WHEEL_PLATFORM,
                                   WHEEL_PURE, classify_file, judge_pin,
                                   parse_lock, render_lock,
                                   resolve_closure, summarise_lock)

A = 'a' * 64
B = 'b' * 64


class ParseTests(unittest.TestCase):
    def test_comments_and_blank_lines_are_skipped(self):
        pins = parse_lock('# header\n\ntorch==2.10.0 --hash=sha256:' + A + '\n')
        self.assertEqual(pins, [{'name': 'torch', 'version': '2.10.0',
                                 'hashes': [A]}])

    def test_names_are_normalised_so_a_duplicate_cannot_hide(self):
        with self.assertRaisesRegex(ValueError, 'again'):
            parse_lock(f'My_Pkg==1.0 --hash=sha256:{A}\n'
                       f'my-pkg==2.0 --hash=sha256:{B}\n')

    def test_several_hashes_on_one_pin_are_all_kept(self):
        pins = parse_lock(f'x==1 --hash=sha256:{A} --hash=sha256:{B}\n')
        self.assertEqual(pins[0]['hashes'], sorted([A, B]))

    def test_a_line_that_is_not_a_hashed_pin_is_refused_not_skipped(self):
        # A silently skipped line would be a pin nobody checked.
        for line in ('torch==2.10.0', 'torch>=2.10.0 --hash=sha256:' + A,
                     '--find-links /wheels', 'torch==2.10.0 --hash=md5:abc'):
            with self.subTest(line=line):
                with self.assertRaisesRegex(ValueError, 'not a hashed pin'):
                    parse_lock(line + '\n')

    def test_a_continuation_line_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'continuation'):
            parse_lock(f'torch==2.10.0 \\\n    --hash=sha256:{A}\n')

    def test_an_empty_lock_is_refused(self):
        for text in ('', '# only a comment\n', '\n\n'):
            with self.subTest(text=text):
                with self.assertRaisesRegex(ValueError, 'no pins'):
                    parse_lock(text)


class ClassifyTests(unittest.TestCase):
    def test_artifact_kinds(self):
        self.assertEqual(classify_file('t-2.10.0.tar.gz', 'sdist'), SDIST)
        self.assertEqual(classify_file('t-2.10.0-py3-none-any.whl', 'bdist_wheel'),
                         WHEEL_PURE)
        self.assertEqual(
            classify_file('t-2.10.0-cp312-cp312-manylinux_2_28_x86_64.whl',
                          'bdist_wheel'), WHEEL_PLATFORM)

    def test_an_sdist_is_reported_even_when_the_digest_matches(self):
        # An sdist pin means the image compiles that package during the build,
        # which for something torch-sized is a different proposition.
        row = judge_pin({'name': 't', 'version': '1', 'hashes': [A]},
                        [{'filename': 't-1.tar.gz', 'packagetype': 'sdist',
                          'digests': {'sha256': A}}])
        self.assertEqual(row['outcome'], SATISFIED)
        self.assertEqual(row['artifact'], SDIST)


class JudgeTests(unittest.TestCase):
    def pin(self):
        return {'name': 'torch', 'version': '2.10.0', 'hashes': [A]}

    def test_an_exact_digest_match_is_satisfied(self):
        row = judge_pin(self.pin(), [
            {'filename': 'torch-2.10.0-cp312-cp312-manylinux_2_28_x86_64.whl',
             'packagetype': 'bdist_wheel', 'digests': {'sha256': A}}])
        self.assertEqual(row['outcome'], SATISFIED)
        self.assertEqual(row['artifact'], WHEEL_PLATFORM)
        self.assertFalse(row['yanked'])

    def test_the_right_version_with_the_wrong_digest_does_not_pass(self):
        # This is exactly what --require-hashes exists to stop, so accepting it
        # on name and version would defeat the lock.
        row = judge_pin(self.pin(), [
            {'filename': 'torch-2.10.0-cp312-cp312-manylinux_2_28_x86_64.whl',
             'packagetype': 'bdist_wheel', 'digests': {'sha256': B}}])
        self.assertEqual(row['outcome'], DIGEST_ABSENT)
        self.assertIn('none matching', row['reason'])

    def test_a_missing_version_and_a_missing_package_are_different(self):
        self.assertEqual(judge_pin(self.pin(), [])['outcome'], VERSION_ABSENT)
        self.assertEqual(judge_pin(self.pin(), None)['outcome'], NOT_ON_INDEX)
        self.assertIn('wheelhouse', judge_pin(self.pin(), None)['reason'])

    def test_a_yanked_file_is_satisfied_but_flagged(self):
        row = judge_pin(self.pin(), [
            {'filename': 'torch-2.10.0-cp312-cp312-manylinux_2_28_x86_64.whl',
             'packagetype': 'bdist_wheel', 'digests': {'sha256': A},
             'yanked': True}])
        self.assertEqual(row['outcome'], SATISFIED)
        self.assertTrue(row['yanked'])


class SummaryTests(unittest.TestCase):
    def rows(self):
        return [
            judge_pin({'name': 'ok', 'version': '1', 'hashes': [A]},
                      [{'filename': 'ok-1-py3-none-any.whl',
                        'packagetype': 'bdist_wheel',
                        'digests': {'sha256': A}}]),
            judge_pin({'name': 'private', 'version': '2', 'hashes': [A]}, None),
        ]

    def test_a_failing_pin_makes_the_lock_not_installable_and_is_named(self):
        summary = summarise_lock(self.rows())
        self.assertFalse(summary['installable'])
        self.assertEqual([row['name'] for row in summary['failing_pins']],
                         ['private'])
        self.assertEqual(summary['satisfied'], 1)

    def test_artifact_kinds_are_counted_for_satisfied_pins(self):
        summary = summarise_lock(self.rows())
        self.assertEqual(summary['artifact_counts'], {WHEEL_PURE: 1})

    def test_the_summary_never_claims_the_image_works(self):
        summary = summarise_lock(self.rows())
        for word in ('Not a build', 'GPU'):
            self.assertIn(word, summary['scope'])

    def test_an_unknown_outcome_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'Unknown pin outcome'):
            summarise_lock([{'outcome': 'looks_fine'}])

    def test_an_empty_audit_is_refused(self):
        for value in ([], None):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    summarise_lock(value)


if __name__ == '__main__':
    unittest.main()


class ClosureTests(unittest.TestCase):
    """A derived lock must not drop a dependency or invent a version."""

    def test_only_what_the_roots_reach_is_kept(self):
        closure = resolve_closure(
            ['torch'],
            {'torch': ['filelock', 'sympy'], 'sympy': ['mpmath'],
             'vllm': ['torch', 'ray']},
            {'torch', 'filelock', 'sympy', 'mpmath', 'vllm', 'ray'})
        self.assertEqual(closure['keep'],
                         ['filelock', 'mpmath', 'sympy', 'torch'])
        self.assertEqual(closure['gaps'], {})

    def test_a_dependency_cycle_terminates(self):
        closure = resolve_closure(['a'], {'a': ['b'], 'b': ['a']}, {'a', 'b'})
        self.assertEqual(closure['keep'], ['a', 'b'])

    def test_a_dependency_the_lock_does_not_pin_is_a_gap_not_a_silent_drop(self):
        # A lock missing a transitive dependency installs a different
        # environment than it claims to pin.
        closure = resolve_closure(['a'], {'a': ['b', 'c']}, {'a', 'b'})
        self.assertEqual(closure['keep'], ['a', 'b'])
        self.assertEqual(closure['gaps'], {'c': ['a']})

    def test_a_root_outside_the_lock_is_refused_outright(self):
        with self.assertRaisesRegex(ValueError, 'Roots absent'):
            resolve_closure(['missing'], {}, {'a'})

    def test_render_copies_versions_and_digests_verbatim(self):
        pins = [{'name': 'torch', 'version': '2.10.0', 'hashes': [A]},
                {'name': 'vllm', 'version': '0.19.1', 'hashes': [B]}]
        text = render_lock(pins, ['torch'], header='derived for a test')
        self.assertIn(f'torch==2.10.0 --hash=sha256:{A}', text)
        self.assertNotIn('vllm', text)
        self.assertTrue(text.startswith('# derived for a test'))
        # The rendered text must itself parse as a lock, or it cannot be used.
        self.assertEqual(parse_lock(text),
                         [{'name': 'torch', 'version': '2.10.0',
                           'hashes': [A]}])

    def test_render_refuses_a_header_that_says_nothing(self):
        pins = [{'name': 'torch', 'version': '2.10.0', 'hashes': [A]}]
        for header in ('', '   ', '\n'):
            with self.subTest(header=header):
                with self.assertRaisesRegex(ValueError, 'header'):
                    render_lock(pins, ['torch'], header=header)

    def test_render_refuses_to_keep_a_name_it_has_no_pin_for(self):
        pins = [{'name': 'torch', 'version': '2.10.0', 'hashes': [A]}]
        with self.assertRaisesRegex(ValueError, 'absent from the source pins'):
            render_lock(pins, ['torch', 'peft'], header='x')

    def test_multiple_hashes_survive_rendering(self):
        pins = [{'name': 'x', 'version': '1', 'hashes': sorted([A, B])}]
        text = render_lock(pins, ['x'], header='x')
        self.assertEqual(parse_lock(text)[0]['hashes'], sorted([A, B]))
