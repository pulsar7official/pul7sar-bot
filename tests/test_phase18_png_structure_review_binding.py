from __future__ import annotations
import hashlib, json, tempfile, unittest
from pathlib import Path
from tools.phase18_bind_png_structure_to_review_bundle import bind, verify
SOURCE_SHA="a"*40; PNG_SHA="b"*64

def write(path,payload): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def bundle(root):
    b=root/"bundle"; b.mkdir(); c=b/"candidate-1.png"; c.write_bytes(b"fixture")
    write(b/"review-bundle-manifest.json",{"schema":"pul7sar-phase18-first-genuine-golden-v6-review-bundle-v1","branch":"phase18/story-intelligence","candidate":1,"cost_mode":"$0-local","offline_only":True,"source_commit_sha":SOURCE_SHA,"png_sha256":PNG_SHA,"exact_evidence_only":True,"eligible_for_human_visual_review":True,"entries":{"candidate_png":{"path":"candidate-1.png","sha256":hashlib.sha256(c.read_bytes()).hexdigest(),"bytes":c.stat().st_size}},"authoritative_gate":False,"network_download_authorized":False,"generation_authorized":False,"human_visual_review_approved":False,"golden_quality_approved":False,"publication_ready":False,"seeds_2_to_4_authorized":False}); return b
def evidence(root,**overrides):
    p={"schema":"pul7sar-phase18-first-genuine-golden-png-structure-v3","status":"FIRST_GENUINE_GOLDEN_PNG_STRUCTURE_VERIFIED","branch":"phase18/story-intelligence","candidate":1,"cost_mode":"$0-local","offline_only":True,"source_commit_sha":SOURCE_SHA,"png_sha256":PNG_SHA,"png_bytes":123,"png_structure_verified":True,"crc_verified_for_all_chunks":True,"idat_zlib_stream_verified":True,"zlib_stream_terminated_exactly":True,"decoded_scanline_layout_verified":True,"scanline_filter_bytes_verified":True,"iend_terminal":True,"no_trailing_bytes":True,"bit_depth":8,"color_type":2,"channels":3,"bits_per_pixel":24,"interlace_method":0,"canonical_encoding_verified":True,"canonical_encoding":"RGB8_TRUECOLOUR_NON_INTERLACED","eligible_for_human_visual_review":True,"authoritative_gate":False,"network_download_authorized":False,"generation_authorized":False,"human_visual_review_approved":False,"golden_quality_approved":False,"publication_ready":False,"seeds_2_to_4_authorized":False}; p.update(overrides); f=root/"structure.json"; write(f,p); return f
class Tests(unittest.TestCase):
    def test_v3_binds_and_replays(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t); b=bundle(r); out=bind(b,evidence(r)); self.assertTrue(out["png_structure_verified"]); self.assertTrue(out["canonical_encoding_verified"]); self.assertEqual(verify(b)["png_sha256"],PNG_SHA)
    def test_rejects_stale_v2(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t)
            with self.assertRaisesRegex(RuntimeError,"SCHEMA_DRIFT"): bind(bundle(r),evidence(r,schema="pul7sar-phase18-first-genuine-golden-png-structure-v2"))
    def test_rejects_missing_canonical_proof(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t)
            with self.assertRaisesRegex(RuntimeError,"canonical_encoding_verified"): bind(bundle(r),evidence(r,canonical_encoding_verified=False))
    def test_rejects_rgba(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t)
            with self.assertRaisesRegex(RuntimeError,"CANONICAL_ENCODING_DRIFT:color_type"): bind(bundle(r),evidence(r,color_type=6,channels=4,bits_per_pixel=32))
    def test_rejects_authority_drift(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t)
            with self.assertRaisesRegex(RuntimeError,"AUTHORITY_DRIFT:structure:publication_ready"): bind(bundle(r),evidence(r,publication_ready=True))
    def test_rejects_bound_byte_drift(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t); b=bundle(r); bind(b,evidence(r)); p=b/"evidence/png_structure.json"; p.write_text(p.read_text()+" ")
            with self.assertRaisesRegex(RuntimeError,"EVIDENCE_DRIFT"): verify(b)
if __name__=="__main__": unittest.main()
