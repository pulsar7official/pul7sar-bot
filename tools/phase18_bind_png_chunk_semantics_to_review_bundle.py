#!/usr/bin/env python3
"""Bind/replay Candidate 1 PNG chunk-semantics evidence into the Golden review bundle.

Fail-closed, CPU-safe, stdlib-only. This grants no review, Golden, publication,
or Seeds 2-4 authority. The semantic evidence is cryptographically chained to
the exact structure-v3 evidence already present in the same review bundle.
"""
from __future__ import annotations
import argparse, hashlib, json, re, shutil
from pathlib import Path

BRANCH="phase18/story-intelligence"
SEMANTICS_SCHEMA="pul7sar-phase18-first-genuine-golden-png-chunk-semantics-v1"
STRUCTURE_SCHEMA="pul7sar-phase18-first-genuine-golden-png-structure-v3"
BUNDLE_SCHEMA="pul7sar-phase18-first-genuine-golden-v6-review-bundle-v1"
ENTRY="evidence_png_chunk_semantics"; ENTRY_PATH="evidence/png_chunk_semantics.json"
UPSTREAM_ENTRY="evidence_png_structure"; UPSTREAM_PATH="evidence/png_structure.json"
CLOSED=("authoritative_gate","network_download_authorized","generation_authorized","human_visual_review_approved","golden_quality_approved","publication_ready","seeds_2_to_4_authorized")

def load(p:Path):
    try: v=json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc: raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_INVALID_JSON") from exc
    if not isinstance(v,dict): raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_INVALID_OBJECT")
    return v

def sha(p:Path): return hashlib.sha256(p.read_bytes()).hexdigest()
def closed(v,label):
    for f in CLOSED:
        if v.get(f) is not False: raise RuntimeError(f"PNG_CHUNK_SEMANTICS_REVIEW_BIND_AUTHORITY_DRIFT:{label}:{f}")

def manifest(v):
    if v.get("schema")!=BUNDLE_SCHEMA: raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_BUNDLE_SCHEMA_DRIFT")
    if v.get("branch")!=BRANCH or v.get("candidate")!=1: raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_BUNDLE_IDENTITY_DRIFT")
    if v.get("cost_mode")!="$0-local" or v.get("offline_only") is not True or v.get("exact_evidence_only") is not True or v.get("eligible_for_human_visual_review") is not True: raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_BUNDLE_POLICY_DRIFT")
    closed(v,"bundle"); source=v.get("source_commit_sha"); png=v.get("png_sha256"); entries=v.get("entries")
    if not re.fullmatch(r"[0-9a-f]{40}",str(source or "")): raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_SOURCE_SHA_INVALID")
    if not re.fullmatch(r"[0-9a-f]{64}",str(png or "")): raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_PNG_SHA_INVALID")
    if not isinstance(entries,dict) or not entries: raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_ENTRIES_INVALID")
    return source,png,entries

def semantics(v,source,png):
    if v.get("schema")!=SEMANTICS_SCHEMA or v.get("status")!="FIRST_GENUINE_GOLDEN_PNG_CHUNK_SEMANTICS_VERIFIED": raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_SCHEMA_DRIFT")
    if v.get("branch")!=BRANCH or v.get("candidate")!=1 or v.get("source_commit_sha")!=source or v.get("png_sha256")!=png: raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_UPSTREAM_IDENTITY_DRIFT")
    if v.get("cost_mode")!="$0-local" or v.get("offline_only") is not True or v.get("eligible_for_human_visual_review") is not True: raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_POLICY_DRIFT")
    for f in ("known_critical_chunks_only","reserved_bit_valid_for_all_chunks","idat_consecutive","plte_order_valid"):
        if v.get(f) is not True: raise RuntimeError(f"PNG_CHUNK_SEMANTICS_REVIEW_BIND_FLAG_DRIFT:{f}")
    if not isinstance(v.get("png_bytes"),int) or v["png_bytes"]<=0: raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_PNG_BYTES_INVALID")
    seq=v.get("chunk_sequence")
    if not isinstance(seq,list) or len(seq)<3 or seq[0]!="IHDR" or seq[-1]!="IEND" or "IDAT" not in seq: raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_CHUNK_SEQUENCE_INVALID")
    closed(v,"semantics")

def upstream_structure(bundle:Path,entries:dict,source:str,png:str):
    r=entries.get(UPSTREAM_ENTRY)
    if not isinstance(r,dict) or r.get("path")!=UPSTREAM_PATH: raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_STRUCTURE_ENTRY_MISSING")
    p=(bundle/UPSTREAM_PATH).resolve()
    try: p.relative_to(bundle)
    except ValueError as exc: raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_STRUCTURE_OUTSIDE_BUNDLE") from exc
    if not p.is_file() or p.stat().st_size!=r.get("bytes") or sha(p)!=r.get("sha256"): raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_STRUCTURE_EVIDENCE_DRIFT")
    v=load(p)
    if v.get("schema")!=STRUCTURE_SCHEMA or v.get("source_commit_sha")!=source or v.get("png_sha256")!=png or v.get("png_structure_verified") is not True or v.get("canonical_encoding_verified") is not True: raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_STRUCTURE_PROOF_DRIFT")
    closed(v,"structure")
    return r["sha256"]

def verify(bundle_dir:Path):
    bundle=bundle_dir.resolve(); mp=bundle/"review-bundle-manifest.json"; m=load(mp); source,png,entries=manifest(m); upstream=upstream_structure(bundle,entries,source,png)
    if m.get("png_chunk_semantics_verified") is not True: raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_VERIFICATION_FLAG_MISSING")
    r=entries.get(ENTRY)
    if not isinstance(r,dict) or r.get("path")!=ENTRY_PATH: raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_ENTRY_MISSING")
    p=(bundle/ENTRY_PATH).resolve()
    try: p.relative_to(bundle)
    except ValueError as exc: raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_ENTRY_OUTSIDE_BUNDLE") from exc
    if not p.is_file() or p.stat().st_size!=r.get("bytes") or sha(p)!=r.get("sha256"): raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_EVIDENCE_DRIFT")
    if m.get("png_chunk_semantics_evidence_sha256")!=r.get("sha256") or m.get("png_chunk_semantics_upstream_structure_evidence_sha256")!=upstream: raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_MANIFEST_SHA_DRIFT")
    semantics(load(p),source,png)
    return {"schema":"pul7sar-phase18-png-chunk-semantics-review-binding-v1","status":"FIRST_GENUINE_GOLDEN_PNG_CHUNK_SEMANTICS_EVIDENCE_BOUND_AND_VERIFIED","branch":BRANCH,"candidate":1,"cost_mode":"$0-local","offline_only":True,"source_commit_sha":source,"png_sha256":png,"png_chunk_semantics_verified":True,"png_chunk_semantics_evidence_sha256":r["sha256"],"upstream_structure_evidence_sha256":upstream,"publication_ready":False,"seeds_2_to_4_authorized":False}

def bind(bundle_dir:Path,semantics_path:Path):
    bundle=bundle_dir.resolve(); mp=bundle/"review-bundle-manifest.json"; m=load(mp); source,png,entries=manifest(m); upstream=upstream_structure(bundle,entries,source,png); semantics(load(semantics_path),source,png)
    if ENTRY in entries: raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_ENTRY_ALREADY_PRESENT")
    dst=bundle/ENTRY_PATH
    if dst.exists(): raise RuntimeError("PNG_CHUNK_SEMANTICS_REVIEW_BIND_DESTINATION_ALREADY_PRESENT")
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(semantics_path,dst); h=sha(dst)
    entries[ENTRY]={"path":ENTRY_PATH,"sha256":h,"bytes":dst.stat().st_size}; m["entries"]=entries; m["png_chunk_semantics_verified"]=True; m["png_chunk_semantics_evidence_sha256"]=h; m["png_chunk_semantics_upstream_structure_evidence_sha256"]=upstream
    tmp=mp.with_suffix(".tmp"); tmp.write_text(json.dumps(m,indent=2,sort_keys=True)+"\n",encoding="utf-8"); tmp.replace(mp); return verify(bundle)

def main():
    p=argparse.ArgumentParser(); s=p.add_subparsers(dest="cmd",required=True); b=s.add_parser("bind"); b.add_argument("--bundle-dir",type=Path,required=True); b.add_argument("--semantics-evidence",type=Path,required=True); v=s.add_parser("verify"); v.add_argument("--bundle-dir",type=Path,required=True); v.add_argument("--output",type=Path); a=p.parse_args(); r=bind(a.bundle_dir,a.semantics_evidence) if a.cmd=="bind" else verify(a.bundle_dir)
    if a.cmd=="verify" and a.output: a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(r,indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
