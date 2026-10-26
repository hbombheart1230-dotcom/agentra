import hashlib
import json
import math
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import importlib.util
import sys
sys.dont_write_bytecode = True
SOURCE = Path(os.environ.get("AGENTRA_RF033_SOURCE", "libs/reporting/baseline_btc_woori_tech/vnext/storage.py"))
assert SOURCE.exists(), f"Missing exact source: {SOURCE}"
spec = importlib.util.spec_from_file_location("rf033_exact_storage", SOURCE)
storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(storage)

class StorageBoundary(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.TemporaryDirectory(prefix='agentra-rf033-lead-')
        self.addCleanup(self.root.cleanup)
        self.path = Path(self.root.name) / 'sub' / 'evidence.json'
    def leftovers(self):
        return list(Path(self.root.name).rglob('.q12-*'))
    def test_mutable_atomic_replace(self):
        first={'x':1}; second={'x':2}
        self.assertEqual(storage.publish(self.path, first), first)
        self.assertEqual(storage.publish(self.path, second), second)
        self.assertEqual(storage.read(self.path),second)
        self.assertEqual(self.leftovers(),[])
    def test_immutable_first_publish(self):
        first={'a':3}; self.assertEqual(storage.publish(self.path,first,immutable=True),first)
        self.assertEqual(storage.read(self.path),first)
        self.assertEqual(self.leftovers(),[])
    def test_immutable_no_clobber(self):
        original={'owner':'existing'}; other={'owner':'candidate'}
        storage.publish(self.path,original)
        self.assertEqual(storage.publish(self.path,other,immutable=True),original)
        self.assertEqual(storage.read(self.path),original)
        self.assertEqual(self.leftovers(),[])
    def test_immutable_link_failure_cleanup(self):
        with patch.object(storage.os,'link',side_effect=PermissionError('simulated')):
            with self.assertRaises(PermissionError): storage.publish(self.path,{'a':1},immutable=True)
        self.assertFalse(self.path.exists()); self.assertEqual(self.leftovers(),[])
    def test_mutable_replace_failure_cleanup(self):
        with patch.object(storage.os,'replace',side_effect=OSError('simulated')):
            with self.assertRaises(OSError): storage.publish(self.path,{'a':1})
        self.assertFalse(self.path.exists()); self.assertEqual(self.leftovers(),[])
    def test_nan_rejected_cleanup(self):
        with self.assertRaises(ValueError): storage.publish(self.path,{'bad':float('nan')})
        self.assertFalse(self.path.exists()); self.assertEqual(self.leftovers(),[])
    def test_fsync_failure_cleanup(self):
        with patch.object(storage.os,'fsync',side_effect=OSError('simulated')):
            with self.assertRaises(OSError): storage.publish(self.path,{'a':1})
        self.assertFalse(self.path.exists()); self.assertEqual(self.leftovers(),[])
    def test_encoded_digest_deterministic(self):
        a={'b':2,'a':'한글'}; b={'a':'한글','b':2}
        self.assertEqual(storage.encoded(a),storage.encoded(b))
        self.assertEqual(storage.digest(a),hashlib.sha256(storage.encoded(a)).hexdigest())
    def test_read_missing_error(self):
        with self.assertRaises(FileNotFoundError): storage.read(self.path)
    def test_no_input_mutation(self):
        a={'nested':[{'x':1}]}; before=json.dumps(a,sort_keys=True)
        storage.publish(self.path,a)
        self.assertEqual(json.dumps(a,sort_keys=True),before)
    def test_existing_immutable_collision_bad_json_propagates(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text('{broken',encoding='utf-8')
        with self.assertRaises(json.JSONDecodeError): storage.publish(self.path,{'x':1},immutable=True)
        self.assertEqual(self.path.read_text(encoding='utf-8'),'{broken')
        self.assertEqual(self.leftovers(),[])

if __name__=='__main__':
    unittest.main(verbosity=1)
