import copy
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

from zenithsync.junit_controls import compare_surefire_runs, surefire_outcomes


def report(cases=None, suite='suite'):
    cases = cases if cases is not None else [('C', 'repair', 'pass'), ('C', 'stable', 'pass'), ('C', 'optional', 'skip')]
    root = ET.Element('testsuite', name=suite, tests=str(len(cases)),
                      failures=str(sum(s == 'fail' for _, _, s in cases)),
                      errors=str(sum(s == 'error' for _, _, s in cases)),
                      skipped=str(sum(s == 'skip' for _, _, s in cases)))
    for cls, name, status in cases:
        case = ET.SubElement(root, 'testcase', classname=cls, name=name)
        if status != 'pass':
            ET.SubElement(case, {'fail': 'failure', 'error': 'error', 'skip': 'skipped'}[status])
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def parse(data, code=0):
    return surefire_outcomes({'TEST-suite.xml': data}, exit_code=code)


class SurefireTests(unittest.TestCase):
    def test_pass_skip_failure_and_error_are_distinct(self):
        cases = [('C', 'one', 'pass'), ('C', 'two', 'fail'),
                 ('C', 'three', 'error'), ('C', 'four', 'skip')]
        value = parse(report(cases), 1)
        self.assertEqual({x['name']: x['status'] for x in value['cases']},
                         {name: status for _, name, status in cases})
        self.assertFalse(value['training_approved'])

    def test_counts_and_exit_status_must_agree(self):
        for key in ('tests', 'failures', 'errors', 'skipped'):
            for invalid in ('-1', '1.0', '01', 'true', '100001', '99999999999999999', '4'):
                root = ET.fromstring(report()); root.set(key, invalid)
                with self.subTest(key=key, value=invalid), self.assertRaises(ValueError):
                    parse(ET.tostring(root))
            root = ET.fromstring(report()); del root.attrib[key]
            with self.assertRaises(ValueError):
                parse(ET.tostring(root))
        for value in (True, -1, 256, '0', None, 1):
            with self.subTest(exit_code=value), self.assertRaises(ValueError):
                parse(report(), value)
        with self.assertRaises(ValueError):
            parse(report([('C', 'bad', 'fail')]), 0)
        for abnormal_exit in (2, 137, 143, 255):
            with self.subTest(abnormal_exit=abnormal_exit), self.assertRaises(ValueError):
                parse(report([('C', 'bad', 'fail')]), abnormal_exit)

    def test_missing_reports_do_not_become_compilation_test_failures(self):
        for reports in ({}, {'a.xml': b''}, {'a.xml': report([])}):
            with self.subTest(reports=reports), self.assertRaises(ValueError):
                surefire_outcomes(reports, exit_code=1)

    def test_malformed_xml_and_unsupported_roots_reject(self):
        for data in (b'<testsuite>', b'<testsuites/>', b'<testsuite/>', b'junk',
                     b'<testsuite xmlns="urn:other" name="suite"/>'):
            with self.subTest(data=data), self.assertRaises(ValueError):
                parse(data)

    def test_entities_encoding_and_byte_limits_reject(self):
        for data in (b'<!DOCTYPE x [<!ENTITY y "abc">]><testsuite/>',
                     b'<!ENTITY x SYSTEM "file:///etc/passwd">', b'\xff',
                     report().decode().encode('utf-16'),
                     report().replace(b"utf-8", b"iso-8859-1")):
            with self.subTest(data=data), self.assertRaises(ValueError):
                parse(data)
        with patch('zenithsync.junit_controls.MAX_REPORT_BYTES', 10):
            with self.assertRaises(ValueError):
                parse(report())
        with patch('zenithsync.junit_controls.MAX_REPORTS', 1):
            with self.assertRaises(ValueError):
                surefire_outcomes({'a.xml': report(), 'b.xml': report(suite='other')}, exit_code=0)
        with patch('zenithsync.junit_controls.MAX_CASES', 2):
            with self.assertRaises(ValueError):
                parse(report())

    def test_duplicate_identity_within_and_across_reports_rejects(self):
        with self.assertRaises(ValueError):
            parse(report([('C', 'same', 'pass'), ('C', 'same', 'pass')]))
        with self.assertRaises(ValueError):
            surefire_outcomes({'a.xml': report(), 'b.xml': report(suite='other')}, exit_code=0)
        with self.assertRaises(ValueError):
            surefire_outcomes({'a.xml': report(), 'b.xml': report([('D', 'other', 'pass')])}, exit_code=0)

    def test_pair_identity_does_not_alias_concatenated_names(self):
        cases = [('A#B', 'C', 'pass'), ('A', 'B#C', 'pass')]
        self.assertEqual(len(parse(report(cases))['cases']), 2)

    def test_retry_unknown_nested_and_conflicting_outcomes_reject(self):
        for tag in ('rerunFailure', 'flakyError', 'unknown', 'testsuite'):
            root = ET.fromstring(report()); ET.SubElement(root[0], tag)
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                parse(ET.tostring(root))
        root = ET.fromstring(report()); ET.SubElement(root[-1], 'failure')
        with self.assertRaises(ValueError):
            parse(ET.tostring(root), 1)
        for tag in ('system-out', 'properties'):
            root = ET.fromstring(report()); metadata = ET.SubElement(root, tag)
            ET.SubElement(metadata, 'testcase', classname='hidden', name='case')
            with self.assertRaises(ValueError):
                parse(ET.tostring(root))
        root = ET.fromstring(report()); ET.SubElement(root, 'failure')
        with self.assertRaises(ValueError):
            parse(ET.tostring(root), 1)
        for key, value in (('status', 'notrun'), ('executed', 'false'), ('retries', '1')):
            root = ET.fromstring(report()); root[0].set(key, value)
            with self.subTest(attribute=key), self.assertRaises(ValueError):
                parse(ET.tostring(root))

    def test_missing_case_names_and_nonbytes_reject(self):
        for key in ('classname', 'name'):
            root = ET.fromstring(report()); del root[0].attrib[key]
            with self.assertRaises(ValueError):
                parse(ET.tostring(root))
        for reports in ({'a.xml': 'text'}, {'../a.xml': report()}, {'a.txt': report()}):
            with self.assertRaises(ValueError):
                surefire_outcomes(reports, exit_code=0)

    def test_unordered_reports_have_stable_output(self):
        a = report([('A', 'one', 'pass')], 'a')
        b = report([('B', 'two', 'pass')], 'b')
        self.assertEqual(surefire_outcomes({'a.xml': a, 'b.xml': b}, exit_code=0),
                         surefire_outcomes({'b.xml': b, 'a.xml': a}, exit_code=0))

    def test_explicit_transition_partition_and_skips(self):
        runs = {role: {'reports': {'a.xml': report([
            ('C', 'repair', 'fail' if role == 'base' else 'pass'),
            ('C', 'stable', 'pass'), ('C', 'optional', 'skip')])},
                       'exit_code': int(role == 'base')}
                for role in ('base', 'reference', 'candidate')}
        expected = dict(fail_to_pass=[['C', 'repair']], pass_to_pass=[['C', 'stable']],
                        skipped=[['C', 'optional']])
        result = compare_surefire_runs(runs, **expected)
        self.assertTrue(result['transitions_verified'])
        self.assertEqual(result['skipped_count'], 1)
        self.assertFalse(result['training_approved'])
        for mutation in ('missing', 'compile', 'unobserved', 'skip_as_pass', 'class_label', 'duplicate'):
            changed, labels = copy.deepcopy(runs), copy.deepcopy(expected)
            if mutation == 'missing': del changed['candidate']
            elif mutation == 'compile': changed['base']['reports'] = {}
            elif mutation == 'unobserved': labels['pass_to_pass'].append(['C', 'missing'])
            elif mutation == 'skip_as_pass':
                labels['skipped'] = []; labels['pass_to_pass'].append(['C', 'optional'])
            elif mutation == 'class_label': labels['fail_to_pass'] = ['C']
            else: labels['fail_to_pass'].append(['C', 'repair'])
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                compare_surefire_runs(changed, **labels)


if __name__ == '__main__':
    unittest.main()
