"""Regression tests with fictional media; no rendering or listening claims."""
import copy
import json
import unittest
from pathlib import Path
from audit_timeline_contract import validate

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.d=json.loads((Path(__file__).resolve().parents[1]/'references/timeline-review-contract.example.json').read_text())
    def test_example(self): self.assertEqual(validate(self.d), [])
    def test_early_flower_exit(self):
        self.d['overlays'][0]['end']=3
        self.assertTrue(any('must end with subtitle' in e for e in validate(self.d)))
    def test_sequential_emphasis(self):
        a=self.d['overlays'][0]; a.update(start=0,end=1,exit_mode='explicit',exit_reason='first thought completes')
        b=copy.deepcopy(a);b.update(id='second',start=1,end=2)
        self.d['overlays'].append(b)
        self.assertEqual(validate(self.d), [])
    def test_simultaneous_emphasis(self):
        b=copy.deepcopy(self.d['overlays'][0]);b['id']='second';self.d['overlays'].append(b)
        self.assertTrue(any('simultaneous emphasis' in e for e in validate(self.d)))
    def test_speech_overlap(self):
        b=copy.deepcopy(self.d['speech'][0]);b.update(id='second',start=3,end=5);self.d['speech'].append(b)
        self.assertTrue(any('speech overlap' in e for e in validate(self.d)))
    def test_subtitle_before_speech(self):
        self.d['subtitles'][0]['start']=0
        self.assertTrue(any('matching speech' in e for e in validate(self.d)))
    def test_wrong_visual_owner(self):
        self.d['subtitles'][0]['owner_scene_id']='scene-waterfall'
        self.assertTrue(any('visual owner' in e for e in validate(self.d)))
    def test_wrong_speech_binding(self):
        self.d['subtitles'][0]['speech_id']='missing'
        self.assertTrue(any('matching speech' in e for e in validate(self.d)))
    def test_early_new_music(self):
        self.d['music'][0]['owner_scene_ids']=['scene-waterfall']
        self.assertTrue(any('before its first owner' in e for e in validate(self.d)))
    def test_multifocus(self):
        self.d['transitions'][0]['moving_focus_layers']=['IMG_001','IMG_002']
        self.assertTrue(any('focus layers' in e for e in validate(self.d)))
    def test_bad_time(self):
        self.d['scenes'][0]['end']=float('nan')
        self.assertTrue(validate(self.d))
    def test_missing_field(self):
        del self.d['scenes'][0]['end'];self.assertTrue(validate(self.d))
    def test_empty(self): self.assertTrue(validate({'fps':24}))
    def test_invalid_fps(self):
        for value in [0,'unknown',float('inf')]:
            self.d['fps']=value;self.assertTrue(validate(self.d))
if __name__=='__main__': unittest.main()
