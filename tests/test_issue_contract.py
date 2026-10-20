from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from zenithsync.issue_contract import assess_issue_contract


class IssueContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.contract = {role:self.root/(role+'.xml') for role in ('base','reference','candidate')}
        self.compatibility = {role:self.root/('compat-'+role+'.xml') for role in ('base','candidate')}
        for role in self.contract:
            self.write(self.contract[role], {'a':'passed' if role == 'candidate' else 'failed'})
        self.write(self.compatibility['base'], {'old':'passed','stable':'passed','missing':'skipped'})
        self.write(self.compatibility['candidate'], {'old':'failed','stable':'passed','missing':'skipped'})
        self.changes = [{'test':'T::old','rationale':'The issue changes the denominator.', 'contract_cases':['T::a']}]

    @staticmethod
    def write(path, cases):
        suite = ET.Element('testsuite', tests=str(len(cases)))
        for name,state in cases.items():
            case = ET.SubElement(suite,'testcase',classname='T',name=name)
            if state != 'passed':ET.SubElement(case,{'failed':'failure','error':'error','skipped':'skipped'}[state])
        ET.ElementTree(suite).write(path)

    def assess(self):
        return assess_issue_contract(contract_reports=self.contract,compatibility_reports=self.compatibility,
                                     contract_cases=['T::a'],declared_changes=self.changes)

    def test_declared_failure_and_skip_remain_visible(self):
        before = {p:p.read_bytes() for p in self.root.iterdir()}
        result = self.assess()
        self.assertTrue(result['contract_checks_passed'])
        self.assertTrue(result['declared_transition_policy_satisfied'])
        self.assertFalse(result['all_compatibility_cases_passed'])
        self.assertFalse(result['reference_equivalent_on_contract'])
        self.assertFalse(result['training_approved'])
        self.assertEqual(result['unresolved_compatibility_cases'],{'T::missing':'skipped','T::old':'failed'})
        self.assertEqual(before,{p:p.read_bytes() for p in self.root.iterdir()})

    def test_unexpected_change_blocks_even_with_contract_pass(self):
        self.write(self.compatibility['candidate'],{'old':'failed','stable':'error','missing':'skipped'})
        result = self.assess()
        self.assertFalse(result['declared_transition_policy_satisfied'])
        self.assertEqual(result['unexpected_compatibility_changes'][0]['test'],'T::stable')

    def test_skip_cannot_be_declared_as_intentional_failure(self):
        self.write(self.compatibility['candidate'],{'old':'skipped','stable':'passed','missing':'skipped'})
        with self.assertRaisesRegex(ValueError,'passed-to-failed'):self.assess()

    def test_missing_or_extra_coverage_rejected(self):
        self.write(self.contract['candidate'],{'a':'passed','extra':'passed'})
        with self.assertRaisesRegex(ValueError,'coverage'):self.assess()
        self.write(self.contract['candidate'],{'a':'passed'})
        self.write(self.compatibility['candidate'],{'old':'failed','stable':'passed'})
        with self.assertRaisesRegex(ValueError,'coverage'):self.assess()

    def test_contract_skip_or_baseline_pass_is_not_reproduction(self):
        for role,state in [('candidate','skipped'),('base','passed')]:
            with self.subTest(role=role):
                original = self.contract[role].read_bytes()
                self.write(self.contract[role],{'a':state})
                self.assertFalse(self.assess()['contract_checks_passed'])
                self.contract[role].write_bytes(original)

    def test_unlinked_empty_or_duplicate_declaration_rejected(self):
        original = self.changes[0]
        for changes in [[original,original],[{**original,'rationale':' '}],
                        [{**original,'contract_cases':['T::invented']}]]:
            self.changes = changes
            with self.assertRaisesRegex(ValueError,'declarations'):self.assess()

    def test_undeclared_regression_stays_unexpected(self):
        self.changes = []
        result = self.assess()
        self.assertFalse(result['declared_transition_policy_satisfied'])
        self.assertEqual(len(result['unexpected_compatibility_changes']),1)


if __name__ == '__main__':unittest.main()
