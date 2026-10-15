from copy import deepcopy
import hashlib
import unittest
from zenithsync.probe_receipt import verify_probe_receipt


class ProbeReceiptTests(unittest.TestCase):
    def setUp(self):
        self.probe = "print('synthetic fixture')\n"
        self.runtime = dict(image='sha256:'+'a'*64, platform='linux/arm64', python='/usr/local/bin/python')
        self.receipt = dict(image=self.runtime['image'], image_id=self.runtime['image'],
                            platform=self.runtime['platform'], entrypoint=self.runtime['python'],
                            probe_source=dict(sha256=hashlib.sha256(self.probe.encode()).hexdigest(), size_bytes=len(self.probe.encode())),
                            generated_grading_tests_executed=True, agent_executed=False,
                            returncode=0, copy_returncode=0, cleanup_returncode=0,
                            state=dict(Status='exited', ExitCode=0, OOMKilled=False, Error=''))

    def test_exact_receipt_and_source_without_mutation(self):
        before=deepcopy(self.receipt)
        self.assertEqual(verify_probe_receipt(self.receipt,self.probe,**self.runtime),self.receipt['probe_source'])
        self.assertEqual(before,self.receipt)

    def test_changed_program_or_runtime_rejects(self):
        with self.assertRaises(ValueError):verify_probe_receipt(self.receipt,self.probe+'print(1)',**self.runtime)
        for key,value in [('image','sha256:'+'b'*64),('image_id','sha256:'+'b'*64),('platform','linux/amd64'),('entrypoint','/other/python'),('generated_grading_tests_executed',False),('agent_executed',True)]:
            r=deepcopy(self.receipt);r[key]=value
            with self.assertRaises(ValueError):verify_probe_receipt(r,self.probe,**self.runtime)

    def test_failure_missing_fields_and_boolean_codes_reject(self):
        for key in ('returncode','copy_returncode','cleanup_returncode'):
            for value in (None,False,1,-9):
                r=deepcopy(self.receipt);r[key]=value
                with self.assertRaises(ValueError):verify_probe_receipt(r,self.probe,**self.runtime)
        for key,value in [('Status','running'),('ExitCode',False),('ExitCode',1),('OOMKilled',True),('Error','failure')]:
            r=deepcopy(self.receipt);r['state'][key]=value
            with self.assertRaises(ValueError):verify_probe_receipt(r,self.probe,**self.runtime)
