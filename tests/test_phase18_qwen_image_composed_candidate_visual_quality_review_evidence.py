from __future__ import annotations

import hashlib, json
from pathlib import Path
import tempfile, unittest
from unittest.mock import patch

from engine.intelligence.golden_visual_quality import GoldenVisualBlockers, GoldenVisualScores
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_evidence import (
    EVIDENCE_SCHEMA, build_composed_candidate_visual_quality_review_evidence,
    verify_composed_candidate_visual_quality_review_evidence,
)
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_request import SCHEMA as CS274_SCHEMA
from engine.intelligence.qwen_image_inference_measurement import sha256_json

class VisualQualityReviewEvidenceTests(unittest.TestCase):
    def _fixture(self, root:Path):
        (root/"artifacts").mkdir(); png=root/"artifacts/composed_candidate.png"; png.write_bytes(b"\x89PNG\r\n\x1a\nfixture")
        comp={"repository_relative_path":"artifacts/composed_candidate.png","sha256":hashlib.sha256(png.read_bytes()).hexdigest(),"byte_size":len(png.read_bytes()),"width":1080,"height":1350}
        request_path=root/"artifacts/cs274.json"; request_path.write_text("{}\n",encoding="utf-8")
        score_names=list(GoldenVisualScores.__dataclass_fields__); blocker_names=list(GoldenVisualBlockers.__dataclass_fields__)
        request={"schema":CS274_SCHEMA,"receipt_sha256":"c"*64,"story_snapshot_sha256":"a"*64,"composed_candidate_png":comp,"golden_visual_quality_contract":{"score_fields":score_names,"blocker_fields":blocker_names,"golden_weighted_floor":8.5,"golden_core_floor":8.0,"elite_target":9.0},"visual_quality_review_requested":True,"visual_quality_review_executed":False,"composition_executed":True,"composed_candidate_bytes_admitted_for_post_composition_qa":True,"semantic_inspection_executed":True,"hybrid_surface_semantic_qa_approved":True,"visual_quality_review_approved":False,"composed_visual_approved":False,"semantic_approved":False,"human_visual_review_approved":False,"genuine_golden_png_created":False,"golden_quality_approved":False,"publication_ready":False}
        evidence={"schema":EVIDENCE_SCHEMA,"story_snapshot_sha256":"a"*64,"composed_candidate_png_sha256":comp["sha256"],"review_request_receipt_sha256":"c"*64,"review_method":"manual_visual_quality_review","reviewer_id":"reviewer-fixture","review_notes":"Independent visual inspection fixture.","scores":{k:8.8 for k in score_names},"blockers":{k:False for k in blocker_names}}
        ev=root/"artifacts/review.json"; ev.write_text(json.dumps(evidence),encoding="utf-8")
        return request_path,ev,request

    def test_admits_complete_evidence_without_golden_authority(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); req,ev,source=self._fixture(root)
            target="engine.intelligence.qwen_image_composed_candidate_visual_quality_review_evidence.verify_composed_candidate_visual_quality_review_request"
            with patch(target,return_value=source):
                p=build_composed_candidate_visual_quality_review_evidence(req,ev,root/"out",repo_root=root)
                r=verify_composed_candidate_visual_quality_review_evidence(p,repo_root=root)
            self.assertTrue(r["visual_quality_review_executed"]); self.assertTrue(r["visual_quality_evidence_admitted"])
            self.assertEqual(r["weighted_score"],8.8); self.assertFalse(r["golden_quality_approved"]); self.assertFalse(r["publication_ready"])

    def test_rejects_incomplete_score_set(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); req,ev,source=self._fixture(root); data=json.loads(ev.read_text()); data["scores"].pop("editorial_realism"); ev.write_text(json.dumps(data))
            with patch("engine.intelligence.qwen_image_composed_candidate_visual_quality_review_evidence.verify_composed_candidate_visual_quality_review_request",return_value=source):
                with self.assertRaisesRegex(ValueError,"SCORE_SET_INVALID"): build_composed_candidate_visual_quality_review_evidence(req,ev,root/"out",repo_root=root)

    def test_rejects_out_of_range_score(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); req,ev,source=self._fixture(root); data=json.loads(ev.read_text()); data["scores"]["editorial_realism"]=10.5; ev.write_text(json.dumps(data))
            with patch("engine.intelligence.qwen_image_composed_candidate_visual_quality_review_evidence.verify_composed_candidate_visual_quality_review_request",return_value=source):
                with self.assertRaisesRegex(ValueError,"SCORE_VALUE_INVALID"): build_composed_candidate_visual_quality_review_evidence(req,ev,root/"out",repo_root=root)

    def test_rejects_external_evidence_byte_drift(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); req,ev,source=self._fixture(root); target="engine.intelligence.qwen_image_composed_candidate_visual_quality_review_evidence.verify_composed_candidate_visual_quality_review_request"
            with patch(target,return_value=source):
                p=build_composed_candidate_visual_quality_review_evidence(req,ev,root/"out",repo_root=root); ev.write_text("{}")
                with self.assertRaisesRegex(ValueError,"EXTERNAL_INVALID_BYTE_DRIFT"): verify_composed_candidate_visual_quality_review_evidence(p,repo_root=root)

    def test_rejects_candidate_byte_drift(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); req,ev,source=self._fixture(root); target="engine.intelligence.qwen_image_composed_candidate_visual_quality_review_evidence.verify_composed_candidate_visual_quality_review_request"
            with patch(target,return_value=source):
                p=build_composed_candidate_visual_quality_review_evidence(req,ev,root/"out",repo_root=root); (root/"artifacts/composed_candidate.png").write_bytes(b"drift")
                with self.assertRaisesRegex(ValueError,"COMPOSED_INVALID_BYTE_DRIFT"): verify_composed_candidate_visual_quality_review_evidence(p,repo_root=root)

    def test_rejects_premature_golden_authority(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); req,ev,source=self._fixture(root); target="engine.intelligence.qwen_image_composed_candidate_visual_quality_review_evidence.verify_composed_candidate_visual_quality_review_request"
            with patch(target,return_value=source):
                p=build_composed_candidate_visual_quality_review_evidence(req,ev,root/"out",repo_root=root); r=json.loads(p.read_text()); r["golden_quality_approved"]=True; u=dict(r); u.pop("receipt_sha256",None); r["receipt_sha256"]=sha256_json(u); p.write_text(json.dumps(r))
                with self.assertRaisesRegex(ValueError,"PREMATURE_AUTHORITY"): verify_composed_candidate_visual_quality_review_evidence(p,repo_root=root)

if __name__=="__main__": unittest.main()
