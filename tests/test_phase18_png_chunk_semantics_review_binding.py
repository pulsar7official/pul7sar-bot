from __future__ import annotations
import hashlib, json, tempfile, unittest
from pathlib import Path
from tools.phase18_bind_png_chunk_semantics_to_review_bundle import bind, verify
SOURCE_SHA="a"*40; PNG_SHA="b"*64

def write(path,payload): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def closed(): return {"authoritative_gate":False,"network_download_authorized":False,"generation_authorized":False,"human_visual_review_approved":False,"golden_quality_approved":False,"publication_ready":False,"seeds_2_to_4_authorized":False}
def bundle(root):
    b=root/"bundle"; b.mkdir(); c=b/"candidate-1.png"; c.write_bytes(b"fixture")
    s=b/"evidence/png_structure.json"; sp={"schema":"pul7sar-phase18-first-genuine-golden-png-structure-v3","branch":"phase18/story-intelligence","candidate":1,"source_commit_sha":SOURCE_SHA,"png_sha256":PNG_SHA,"png_structure_verified":True,"canonical_encoding_verified":True,**closed()}; write(s,sp)
    write(b/"review-bundle-manifest.json",{"schema":"pul7sar-phase18-first-genuine-golden-v6-review-bundle-v1","branch":"phase18/story-intelligence","candidate":1,"cost_mode":"$0-local","offline_only":True,"source_commit_sha":SOURCE_SHA,"png_sha256":PNG_SHA,"exact_evidence_only":True,"eligible_for_human_visual_review":True,"entries":{"candidate_png":{"path":"candidate-1.png","sha256":hashlib.sha256(c.read_bytes()).hexdigest(),"bytes":c.stat().st_size},"evidence_png_structure":{"path":"evidence/png_structure.json","sha256":hashlib.sha256(s.read_bytes()).hexdigest(),"bytes":s.stat().st_size}},**closed()}); return b
def evidence(root,**overrides):
    p={"schema":"pul7sar-phase18-first-genuine-golden-png-chunk-semantics-v1","status":"FIRST_GENUINE_GOLDEN_PNG_CHUNK_SEMANTICS_VERIFIED","branch":"phase18/story-intelligence","candidate":1,"cost_mode":"$0-local","offline_only":True,"source_commit_sha":SOURCE_SHA,"png_sha256":PNG_SHA,"png_bytes":123,"chunk_sequence":["IHDR","IDAT","IEND"],"known_critical_chunks_only":True,"reserved_bit_valid_for_all_chunks":True,"idat_consecutive":True,"plte_order_valid":True,"eligible_for_human_visual_review":True,**closed()}; p.update(overrides); f=root/"semantics.json"; write(f,p); return f
class Tests(unittest.TestCase):
    def test_binds_and_replays_with_structure_hash_chain(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t); b=bundle(r); out=bind(b,evidence(r)); self.assertTrue(out["png_chunk_semantics_verified"]); self.assertEqual(out["upstream_structure_evidence_sha256"],hashlib.sha256((b/"evidence/png_structure.json").read_bytes()).hexdigest()); self.assertEqual(verify(b)["png_sha256"],PNG_SHA)
    def test_rejects_missing_structure_entry(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t); b=bundle(r); m=json.loads((b/"review-bundle-manifest.json").read_text()); del m["entries"]["evidence_png_structure"]; write(b/"review-bundle-manifest.json",m)
            with self.assertRaisesRegex(RuntimeError,"STRUCTURE_ENTRY_MISSING"): bind(b,evidence(r))
    def test_rejects_structure_byte_drift_on_replay(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t); b=bundle(r); bind(b,evidence(r)); p=b/"evidence/png_structure.json"; p.write_text(p.read_text()+" ")
            with self.assertRaisesRegex(RuntimeError,"STRUCTURE_EVIDENCE_DRIFT"): verify(b)
    def test_rejects_semantics_byte_drift(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t); b=bundle(r); bind(b,evidence(r)); p=b/"evidence/png_chunk_semantics.json"; p.write_text(p.read_text()+" ")
            with self.assertRaisesRegex(RuntimeError,"EVIDENCE_DRIFT"): verify(b)
    def test_rejects_false_semantic_gate(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t)
            with self.assertRaisesRegex(RuntimeError,"FLAG_DRIFT:idat_consecutive"): bind(bundle(r),evidence(r,idat_consecutive=False))
    def test_rejects_authority_drift(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t)
            with self.assertRaisesRegex(RuntimeError,"AUTHORITY_DRIFT:semantics:publication_ready"): bind(bundle(r),evidence(r,publication_ready=True))
if __name__=="__main__": unittest.main()
