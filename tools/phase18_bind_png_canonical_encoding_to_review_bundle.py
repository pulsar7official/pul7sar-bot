#!/usr/bin/env python3
"""Bind/replay canonical RGB8 evidence with an exact upstream structure-evidence hash chain."""
from __future__ import annotations
import argparse, hashlib, json, re, shutil
from pathlib import Path
from typing import Any
EXPECTED_BRANCH="phase18/story-intelligence"; EXPECTED_COST_MODE="$0-local"
CANONICAL_SCHEMA="pul7sar-phase18-first-genuine-golden-png-canonical-encoding-v2"
STRUCTURE_SCHEMA="pul7sar-phase18-first-genuine-golden-png-structure-v3"
BUNDLE_SCHEMA="pul7sar-phase18-first-genuine-golden-v6-review-bundle-v1"
ENTRY_KEY="evidence_png_canonical_encoding"; ENTRY_PATH="evidence/png_canonical_encoding.json"
STRUCTURE_ENTRY_KEY="evidence_png_structure"; STRUCTURE_ENTRY_PATH="evidence/png_structure.json"
AUTHORITY_FIELDS=("authoritative_gate","network_download_authorized","generation_authorized","human_visual_review_approved","golden_quality_approved","publication_ready","seeds_2_to_4_authorized")

def _load(path:Path)->dict[str,Any]:
    try: value=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,UnicodeError,json.JSONDecodeError) as exc: raise RuntimeError(f"PNG_CANONICAL_REVIEW_BIND_INVALID_JSON:{path}") from exc
    if not isinstance(value,dict): raise RuntimeError(f"PNG_CANONICAL_REVIEW_BIND_INVALID_OBJECT:{path}")
    return value

def _sha256(path:Path)->str:
    d=hashlib.sha256()
    with path.open("rb") as h:
        for chunk in iter(lambda:h.read(1024*1024),b""): d.update(chunk)
    return d.hexdigest()

def _require_closed(p:dict[str,Any],label:str)->None:
    for f in AUTHORITY_FIELDS:
        if p.get(f) is not False: raise RuntimeError(f"PNG_CANONICAL_REVIEW_BIND_AUTHORITY_DRIFT:{label}:{f}")

def _verify_manifest(p:dict[str,Any])->tuple[str,str,dict[str,Any]]:
    if p.get("schema")!=BUNDLE_SCHEMA: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_BUNDLE_SCHEMA_DRIFT")
    if p.get("branch")!=EXPECTED_BRANCH or p.get("candidate")!=1: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_BUNDLE_IDENTITY_DRIFT")
    if p.get("cost_mode")!=EXPECTED_COST_MODE or p.get("offline_only") is not True: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_BUNDLE_POLICY_DRIFT")
    if p.get("exact_evidence_only") is not True or p.get("eligible_for_human_visual_review") is not True: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_BUNDLE_ELIGIBILITY_DRIFT")
    _require_closed(p,"bundle"); s=p.get("source_commit_sha"); q=p.get("png_sha256")
    if not re.fullmatch(r"[0-9a-f]{40}",str(s or "")): raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_SOURCE_SHA_INVALID")
    if not re.fullmatch(r"[0-9a-f]{64}",str(q or "")): raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_PNG_SHA_INVALID")
    e=p.get("entries")
    if not isinstance(e,dict) or not e: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_ENTRIES_INVALID")
    return str(s),str(q),e

def _structure_sha(bundle:Path,entries:dict[str,Any])->str:
    record=entries.get(STRUCTURE_ENTRY_KEY)
    if not isinstance(record,dict) or record.get("path")!=STRUCTURE_ENTRY_PATH: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_STRUCTURE_ENTRY_MISSING")
    expected=record.get("sha256"); size=record.get("bytes"); path=(bundle/STRUCTURE_ENTRY_PATH).resolve()
    if not re.fullmatch(r"[0-9a-f]{64}",str(expected or "")) or not isinstance(size,int) or size<=0: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_STRUCTURE_METADATA_INVALID")
    try: path.relative_to(bundle)
    except ValueError as exc: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_STRUCTURE_OUTSIDE_BUNDLE") from exc
    if not path.is_file() or path.stat().st_size!=size or _sha256(path)!=expected: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_STRUCTURE_EVIDENCE_DRIFT")
    structure=_load(path)
    if structure.get("schema")!=STRUCTURE_SCHEMA: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_STRUCTURE_SCHEMA_DRIFT")
    return str(expected)

def _verify_evidence(p:dict[str,Any],source_sha:str,png_sha:str,structure_sha:str)->None:
    if p.get("schema")!=CANONICAL_SCHEMA or p.get("status")!="FIRST_GENUINE_GOLDEN_PNG_CANONICAL_ENCODING_VERIFIED": raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_EVIDENCE_SCHEMA_DRIFT")
    if p.get("branch")!=EXPECTED_BRANCH or p.get("candidate")!=1: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_EVIDENCE_IDENTITY_DRIFT")
    if p.get("cost_mode")!=EXPECTED_COST_MODE or p.get("offline_only") is not True: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_EVIDENCE_POLICY_DRIFT")
    if p.get("source_commit_sha")!=source_sha or p.get("png_sha256")!=png_sha: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_UPSTREAM_IDENTITY_DRIFT")
    if p.get("upstream_structure_schema")!=STRUCTURE_SCHEMA or p.get("upstream_structure_evidence_sha256")!=structure_sha: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_STRUCTURE_HASH_CHAIN_DRIFT")
    expected={"canonical_color_mode":"RGB8","bit_depth":8,"color_type":2,"channels":3,"bits_per_pixel":24,"interlace_method":0,"canonical_platform_encoding_verified":True,"eligible_for_human_visual_review":True}
    for f,v in expected.items():
        if p.get(f)!=v: raise RuntimeError(f"PNG_CANONICAL_REVIEW_BIND_ENCODING_DRIFT:{f}")
    if not isinstance(p.get("png_bytes"),int) or p["png_bytes"]<=0: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_PNG_BYTES_INVALID")
    _require_closed(p,"canonical")

def bind(*,bundle_dir:Path,evidence_path:Path)->dict[str,Any]:
    bundle=bundle_dir.resolve(); manifest_path=bundle/"review-bundle-manifest.json"
    if not manifest_path.is_file(): raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_BUNDLE_MANIFEST_MISSING")
    manifest=_load(manifest_path); source,png,entries=_verify_manifest(manifest); structure_sha=_structure_sha(bundle,entries)
    evidence=_load(evidence_path); _verify_evidence(evidence,source,png,structure_sha)
    if ENTRY_KEY in entries: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_ENTRY_ALREADY_PRESENT")
    destination=bundle/ENTRY_PATH
    if destination.exists(): raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_DESTINATION_ALREADY_PRESENT")
    destination.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(evidence_path,destination); file_sha=_sha256(destination)
    entries[ENTRY_KEY]={"path":ENTRY_PATH,"sha256":file_sha,"bytes":destination.stat().st_size}; manifest["png_canonical_encoding_verified"]=True
    manifest["png_canonical_encoding_evidence_sha256"]=file_sha; manifest["png_canonical_upstream_structure_evidence_sha256"]=structure_sha; manifest["entries"]=entries
    temp=manifest_path.with_name(manifest_path.name+".tmp"); temp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8"); temp.replace(manifest_path)
    return verify(bundle_dir=bundle)

def verify(*,bundle_dir:Path)->dict[str,Any]:
    bundle=bundle_dir.resolve(); manifest_path=bundle/"review-bundle-manifest.json"
    if not manifest_path.is_file(): raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_BUNDLE_MANIFEST_MISSING")
    manifest=_load(manifest_path); source,png,entries=_verify_manifest(manifest); structure_sha=_structure_sha(bundle,entries)
    if manifest.get("png_canonical_encoding_verified") is not True or manifest.get("png_canonical_upstream_structure_evidence_sha256")!=structure_sha: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_STRUCTURE_HASH_CHAIN_DRIFT")
    record=entries.get(ENTRY_KEY)
    if not isinstance(record,dict) or record.get("path")!=ENTRY_PATH: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_ENTRY_MISSING")
    expected,size=record.get("sha256"),record.get("bytes"); path=(bundle/ENTRY_PATH).resolve()
    if not re.fullmatch(r"[0-9a-f]{64}",str(expected or "")) or not isinstance(size,int) or size<=0: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_ENTRY_METADATA_INVALID")
    if not path.is_file() or path.stat().st_size!=size or _sha256(path)!=expected: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_EVIDENCE_DRIFT")
    if manifest.get("png_canonical_encoding_evidence_sha256")!=expected: raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_MANIFEST_SHA_DRIFT")
    _verify_evidence(_load(path),source,png,structure_sha)
    return {"schema":"pul7sar-phase18-png-canonical-encoding-review-binding-v2","status":"FIRST_GENUINE_GOLDEN_PNG_CANONICAL_ENCODING_EVIDENCE_BOUND_AND_VERIFIED","branch":EXPECTED_BRANCH,"candidate":1,"cost_mode":EXPECTED_COST_MODE,"offline_only":True,"source_commit_sha":source,"png_sha256":png,"png_canonical_encoding_verified":True,"png_canonical_encoding_evidence_sha256":str(expected),"upstream_structure_evidence_sha256":structure_sha,"network_download_authorized":False,"human_visual_review_approved":False,"golden_quality_approved":False,"publication_ready":False,"seeds_2_to_4_authorized":False}

def main()->int:
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command",required=True); b=sub.add_parser("bind"); b.add_argument("--bundle-dir",type=Path,required=True); b.add_argument("--canonical-evidence",type=Path,required=True); v=sub.add_parser("verify"); v.add_argument("--bundle-dir",type=Path,required=True); v.add_argument("--output",type=Path); a=p.parse_args()
    result=bind(bundle_dir=a.bundle_dir,evidence_path=a.canonical_evidence) if a.command=="bind" else verify(bundle_dir=a.bundle_dir)
    if a.command=="verify" and a.output is not None: a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
