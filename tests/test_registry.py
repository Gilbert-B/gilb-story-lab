"""Integration tests. Run: python -m unittest discover -s tests -v"""
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'tools'/'registry.py'

class RegistryTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/'stories').mkdir();(self.root/'registry').mkdir()
        (self.root/'registry'/'global.json').write_text('{"records": []}',encoding='utf-8')
    def cmd(self,*args,ok=True):
        result=subprocess.run([sys.executable,str(SCRIPT),'--root',str(self.root),*args],capture_output=True,text=True)
        if ok and result.returncode: self.fail(result.stdout+'\n'+result.stderr)
        return result
    def story_file(self):return self.root/'stories'/'GILB-001'/'record.json'
    def test_lifecycle_and_automatic_exports(self):
        self.cmd('new-story','Test market share story','--pillar','Technology & changing Ghana')
        self.assertTrue(self.story_file().exists())
        self.cmd('add-record','GILB-001','dataset','--field','name=Official subscriptions','--field','publisher=NCA','--field','source_url=https://example.org/data','--field','acquisition_status=Not downloaded')
        self.cmd('add-record','GILB-001','analysis','--field','question=Compute market share','--field','input_dataset_ids=DATA-001','--field','status=Not started')
        self.cmd('add-record','GILB-001','evidence','--field','claim=Operator A has most subscriptions','--field','source_dataset_id=DATA-001','--field','verification_status=Needs verification','--field','safe_to_publish=No')
        self.cmd('set-story','GILB-001','--field','stage=Research underway')
        self.assertEqual(json.loads((self.root/'exports'/'dashboard.json').read_text())['verified_approved_claims'],0)
        with (self.root/'exports'/'STORIES.csv').open(encoding='utf-8-sig',newline='') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(rows[0]['dataset_count'],'1')
        self.assertEqual(rows[0]['analysis_count'],'1')
        self.assertEqual(rows[0]['evidence_count'],'1')
        self.assertTrue((self.root/'exports'/'index.html').exists())
        self.assertEqual(len((self.root/'registry'/'events.jsonl').read_text().splitlines()),5)
        # New IDs are allocated instead of reusing an existing ID.
        self.cmd('new-story','A second idea','--pillar','Sports & competition')
        self.assertTrue((self.root/'stories'/'GILB-002'/'record.json').exists())
    def test_prevent_unverified_publish(self):
        self.cmd('new-story','Unsafe story','--pillar','Sports & competition')
        self.cmd('add-record','GILB-001','evidence','--field','claim=Unverified claim','--field','safe_to_publish=No')
        res=self.cmd('set-story','GILB-001','--field','stage=Published',ok=False)
        self.assertNotEqual(res.returncode,0)
        self.assertEqual(json.loads(self.story_file().read_text())['story']['stage'],'Idea')
    def test_prevent_unapproved_claim(self):
        self.cmd('new-story','An idea','--pillar','Sports & competition')
        res=self.cmd('add-record','GILB-001','evidence','--field','claim=A claim','--field','verification_status=Needs verification','--field','safe_to_publish=Yes',ok=False)
        self.assertNotEqual(res.returncode,0)
        self.assertEqual(len(json.loads(self.story_file().read_text())['evidence']),0)
    def test_publish_with_review_and_url(self):
        self.cmd('new-story','Reviewed','--pillar','Sports & competition')
        self.cmd('add-record','GILB-001','evidence','--field','claim=Claim with proof','--field','source_url=https://example.org/proof','--field','verification_status=Verified','--field','checked_by=GilB','--field','checked_on=2026-11-07','--field','approved_by=GilB','--field','approval_date=2026-11-07','--field','safe_to_publish=Yes')
        self.cmd('add-record','GILB-001','post','--field','publish_status=Published','--field','post_url=https://example.org/post','--field','actual_date=2026-11-07')
        self.cmd('set-story','GILB-001','--field','stage=Published')
        self.assertEqual(json.loads((self.root/'exports'/'dashboard.json').read_text())['published_stories'],1)

if __name__=='__main__':unittest.main()
