from __future__ import annotations
import hashlib,json,tempfile,unittest
from pathlib import Path
from tools.phase18_bind_png_canonical_encoding_to_review_bundle import bind,verify

class CanonicalEncodingReviewBindingTests(unittest.TestCase):
    def _fixture(self,root:Path)->tuple[Path,Path]:
        bundle=root/"bundle"; (bundle/"evidence").mkdir(parents=True); source_sha="a"*40; png_sha="b"*64
        structure={"schema":"pul7sar-phase18-first-genuine-golden-png-structure-v3","source_commit_sha":source_sha,"png_sha256":png_sha}
        sp=bundle/"evidence/png_structure.json"; sp.write_text(json.dumps(structure),encoding="utf-8"); ss=hashlib.sha256(sp.read_bytes()).hexdigest()
        manifest={"schema":"pul7sar-phase18-first-genuine-golden-v6-review-bundle-v1","branch":"phase18/story-intelligence","candidate":1,"cost_mode":"$0-local","offline_only":True,"exact_evidence_only":True,"eligible_for_human_visual_review":True,"source_commit_sha":source_sha,"png_sha256":png_sha,"entries":{"candidate_png":{"path":"candidate.png","sha256":png_sha,"bytes":1},"evidence_png_structure":{"path":"evidence/png_structure.json","sha256":ss,"bytes":sp.stat().st_size}},"authoritative_gate":False,"network_download_authorized":False,"generation_authorized":False,"human_visual_review_approved":False,"golden_quality_approved":False,"publication_ready":False,"seeds_2_to_4_authorized":False}
        (bundle/"review-bundle-manifest.json").write_text(json.dumps(manifest),encoding="utf-8")
        evidence={"schema":"pul7sar-phase18-first-genuine-golden-png-canonical-encoding-v2","status":"FIRST_GENUINE_GOLDEN_PNG_CANONICAL_ENCODING_VERIFIED","branch":"phase18/story-intelligence","candidate":1,"cost_mode":"$0-local","offline_only":True,"source_commit_sha":source_sha,"png_sha256":png_sha,"png_bytes":123,"upstream_structure_schema":"pul7sar-phase18-first-genuine-golden-png-structure-v3","upstream_structure_evidence_sha256":ss,"canonical_color_mode":"RGB8","bit_depth":8,"color_type":2,"channels":3,"bits_per_pixel":24,"interlace_method":0,"canonical_platform_encoding_verified":True,"eligible_for_human_visual_review":True,"authoritative_gate":False,"network_download_authorized":False,"generation_authorized":False,"human_visual_review_approved":False,"golden_quality_approved":False,"publication_ready":False,"seeds_2_to_4_authorized":False}
        ep=root/"canonical.json"; ep.write_text(json.dumps(evidence),encoding="utf-8"); return bundle,ep
    def test_bind_and_replay_preserves_structure_hash_chain(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle,evidence=self._fixture(Path(temp)); result=bind(bundle_dir=bundle,evidence_path=evidence); self.assertTrue(result["png_canonical_encoding_verified"]); self.assertRegex(result["upstream_structure_evidence_sha256"],r"^[0-9a-f]{64}$"); self.assertEqual(verify(bundle_dir=bundle)["status"],"FIRST_GENUINE_GOLDEN_PNG_CANONICAL_ENCODING_EVIDENCE_BOUND_AND_VERIFIED")
    def test_rejects_non_rgb8_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle,evidence=self._fixture(Path(temp)); p=json.loads(evidence.read_text()); p["color_type"]=6; evidence.write_text(json.dumps(p))
            with self.assertRaisesRegex(RuntimeError,"ENCODING_DRIFT:color_type"): bind(bundle_dir=bundle,evidence_path=evidence)
    def test_rejects_structure_hash_chain_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle,evidence=self._fixture(Path(temp)); p=json.loads(evidence.read_text()); p["upstream_structure_evidence_sha256"]="c"*64; evidence.write_text(json.dumps(p))
            with self.assertRaisesRegex(RuntimeError,"STRUCTURE_HASH_CHAIN_DRIFT"): bind(bundle_dir=bundle,evidence_path=evidence)
    def test_replay_rejects_structure_bytes_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle,evidence=self._fixture(Path(temp)); bind(bundle_dir=bundle,evidence_path=evidence); sp=bundle/"evidence/png_structure.json"; sp.write_text(sp.read_text()+"\n")
            with self.assertRaisesRegex(RuntimeError,"STRUCTURE_EVIDENCE_DRIFT"): verify(bundle_dir=bundle)
    def test_rejects_authority_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle,evidence=self._fixture(Path(temp)); p=json.loads(evidence.read_text()); p["publication_ready"]=True; evidence.write_text(json.dumps(p))
            with self.assertRaisesRegex(RuntimeError,"AUTHORITY_DRIFT:canonical:publication_ready"): bind(bundle_dir=bundle,evidence_path=evidence)
    def test_replay_rejects_byte_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle,evidence=self._fixture(Path(temp)); bind(bundle_dir=bundle,evidence_path=evidence); bound=bundle/"evidence/png_canonical_encoding.json"; bound.write_text(bound.read_text()+"\n")
            with self.assertRaisesRegex(RuntimeError,"EVIDENCE_DRIFT"): verify(bundle_dir=bundle)
if __name__=="__main__": unittest.main()
