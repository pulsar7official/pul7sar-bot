"""CS275: admit external visual-quality evidence without granting Golden authority."""
from __future__ import annotations

from dataclasses import asdict, fields
import hashlib, json, os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.golden_visual_quality import GoldenVisualBlockers, GoldenVisualScores
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_request import SCHEMA as CS274_SCHEMA, verify_composed_candidate_visual_quality_review_request
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA="pul7sar-phase18-qwen-image-composed-candidate-visual-quality-review-evidence-v1"
EVIDENCE_SCHEMA="pul7sar-phase18-composed-candidate-visual-quality-external-review-v1"
SCORES=tuple(f.name for f in fields(GoldenVisualScores)); BLOCKERS=tuple(f.name for f in fields(GoldenVisualBlockers))
DOWNSTREAM=("visual_quality_review_approved","composed_visual_approved","semantic_approved","human_visual_review_approved","genuine_golden_png_created","golden_quality_approved","publication_ready")

def _json(p:Path, code:str)->dict[str,Any]:
    if p.is_symlink() or not p.is_file(): raise ValueError(code)
    try: v=json.loads(p.read_text(encoding="utf-8"))
    except (UnicodeDecodeError,json.JSONDecodeError) as e: raise ValueError(code) from e
    if not isinstance(v,dict): raise ValueError(code)
    return v

def _bind(root:Path,p:Path,code:str)->dict[str,Any]:
    if p.is_symlink(): raise ValueError(code)
    rr=root.resolve(); q=p.resolve()
    try: rel=q.relative_to(rr).as_posix()
    except ValueError as e: raise ValueError(code) from e
    if not q.is_file(): raise ValueError(code)
    raw=q.read_bytes()
    if not raw: raise ValueError(code)
    return {"repository_relative_path":rel,"sha256":hashlib.sha256(raw).hexdigest(),"byte_size":len(raw)}

def _reopen(root:Path,b:Mapping[str,Any],code:str)->Path:
    rel=b.get("repository_relative_path")
    if not isinstance(rel,str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts: raise ValueError(code)
    p=root.resolve()/rel; now=_bind(root,p,code)
    if now.get("repository_relative_path")!=b.get("repository_relative_path") or now.get("sha256")!=b.get("sha256") or now.get("byte_size")!=b.get("byte_size"):
        raise ValueError(code+"_BYTE_DRIFT")
    return p

def _request(req:Mapping[str,Any])->None:
    for k in ("visual_quality_review_requested","composition_executed","composed_candidate_bytes_admitted_for_post_composition_qa","semantic_inspection_executed","hybrid_surface_semantic_qa_approved"):
        if req.get(k) is not True: raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_REQUIRED_GATE_MISSING:"+k)
    if req.get("visual_quality_review_executed") is not False: raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_REQUEST_ALREADY_EXECUTED")
    for k in DOWNSTREAM:
        if req.get(k) is not False: raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_PREMATURE_AUTHORITY:"+k)

def _review(ev:Mapping[str,Any],req:Mapping[str,Any]):
    if ev.get("schema")!=EVIDENCE_SCHEMA: raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_SCHEMA_INVALID")
    if ev.get("story_snapshot_sha256")!=req.get("story_snapshot_sha256"): raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_STORY_DRIFT")
    if ev.get("composed_candidate_png_sha256")!=(req.get("composed_candidate_png") or {}).get("sha256"): raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_CANDIDATE_DRIFT")
    if ev.get("review_request_receipt_sha256")!=req.get("receipt_sha256"): raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_REQUEST_RECEIPT_DRIFT")
    if ev.get("review_method")!="manual_visual_quality_review": raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_METHOD_INVALID")
    if not isinstance(ev.get("reviewer_id"),str) or not ev["reviewer_id"].strip(): raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_REVIEWER_MISSING")
    if not isinstance(ev.get("review_notes"),str) or not ev["review_notes"].strip(): raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_NOTES_MISSING")
    sr=ev.get("scores"); br=ev.get("blockers")
    if not isinstance(sr,Mapping) or set(sr)!=set(SCORES): raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_SCORE_SET_INVALID")
    try: s=GoldenVisualScores(**{k:sr[k] for k in SCORES})
    except (TypeError,ValueError) as e: raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_SCORE_VALUE_INVALID") from e
    if not isinstance(br,Mapping) or set(br)!=set(BLOCKERS): raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_BLOCKER_SET_INVALID")
    if any(not isinstance(br[k],bool) for k in BLOCKERS): raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_BLOCKER_VALUE_INVALID")
    b=GoldenVisualBlockers(**{k:br[k] for k in BLOCKERS})
    return {k:float(v) for k,v in asdict(s).items()},dict(asdict(b)),s.weighted_score,list(b.active)

def build_composed_candidate_visual_quality_review_evidence(cs274_request_path:Path,external_review_path:Path,output_dir:Path,*,repo_root:Path)->Path:
    if output_dir.exists() or not output_dir.parent.is_dir(): raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_OUTPUT_INVALID")
    rb=_bind(repo_root,cs274_request_path,"QWEN_VISUAL_QUALITY_EVIDENCE_CS274_INVALID"); eb=_bind(repo_root,external_review_path,"QWEN_VISUAL_QUALITY_EVIDENCE_EXTERNAL_INVALID")
    req=verify_composed_candidate_visual_quality_review_request(cs274_request_path,repo_root=repo_root)
    if req.get("schema")!=CS274_SCHEMA: raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_CS274_SCHEMA_DRIFT")
    _request(req); ev=_json(external_review_path,"QWEN_VISUAL_QUALITY_EVIDENCE_EXTERNAL_INVALID"); s,b,w,a=_review(ev,req)
    contract=req.get("golden_visual_quality_contract") or {}
    if tuple(contract.get("score_fields") or ())!=SCORES or tuple(contract.get("blocker_fields") or ())!=BLOCKERS: raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_CONTRACT_DRIFT")
    out={"schema":SCHEMA,"status":"QWEN_IMAGE_COMPOSED_CANDIDATE_VISUAL_QUALITY_REVIEW_EVIDENCE_ADMITTED","story_snapshot_sha256":req.get("story_snapshot_sha256"),"source_cs274_request":{**rb,"receipt_sha256":req.get("receipt_sha256")},"composed_candidate_png":dict(req.get("composed_candidate_png") or {}),"golden_visual_quality_contract":dict(contract),"external_review_evidence":eb,"review_method":ev.get("review_method"),"reviewer_id":ev.get("reviewer_id"),"scores":s,"blockers":b,"weighted_score":w,"active_blockers":a,"visual_quality_review_requested":True,"visual_quality_review_executed":True,"visual_quality_evidence_admitted":True,"visual_quality_review_approved":False,"composition_executed":True,"composed_candidate_bytes_admitted_for_post_composition_qa":True,"semantic_inspection_executed":True,"hybrid_surface_semantic_qa_approved":True,"composed_visual_approved":False,"semantic_approved":False,"human_visual_review_approved":False,"genuine_golden_png_created":False,"golden_quality_approved":False,"publication_ready":False,"policy":{"external_review_is_admitted_not_generated":True,"semantic_qa_is_not_score_evidence":True,"golden_selector_not_executed_here":True,"human_review_remains_independent":True,"semantic_publication_remains_independent":True}}
    out["receipt_sha256"]=sha256_json(out); output_dir.mkdir(mode=0o700); p=output_dir/"composed_candidate_visual_quality_review_evidence.json"; tmp=output_dir/("."+p.name+".tmp")
    try:
        with tmp.open("x",encoding="utf-8") as h: h.write(json.dumps(out,ensure_ascii=False,separators=(",",":"))+"\n"); h.flush(); os.fsync(h.fileno())
        os.replace(tmp,p)
    except Exception:
        if tmp.exists(): tmp.unlink()
        if output_dir.exists() and not any(output_dir.iterdir()): output_dir.rmdir()
        raise
    return p

def verify_composed_candidate_visual_quality_review_evidence(receipt_path:Path,*,repo_root:Path)->dict[str,Any]:
    r=_json(receipt_path,"QWEN_VISUAL_QUALITY_EVIDENCE_RECEIPT_INVALID"); unsigned=dict(r); claimed=unsigned.pop("receipt_sha256",None)
    if r.get("schema")!=SCHEMA or claimed!=sha256_json(unsigned): raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_RECEIPT_INVALID")
    if r.get("visual_quality_review_executed") is not True or r.get("visual_quality_evidence_admitted") is not True: raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_STATE_DRIFT")
    for k in DOWNSTREAM:
        if r.get(k) is not False: raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_PREMATURE_AUTHORITY:"+k)
    rb=r.get("source_cs274_request"); eb=r.get("external_review_evidence")
    if not isinstance(rb,Mapping) or not isinstance(eb,Mapping): raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_BINDING_INVALID")
    req=verify_composed_candidate_visual_quality_review_request(_reopen(repo_root,rb,"QWEN_VISUAL_QUALITY_EVIDENCE_CS274_INVALID"),repo_root=repo_root); _request(req)
    if rb.get("receipt_sha256")!=req.get("receipt_sha256"): raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_CS274_RECEIPT_DRIFT")
    if r.get("story_snapshot_sha256")!=req.get("story_snapshot_sha256") or r.get("composed_candidate_png")!=req.get("composed_candidate_png") or r.get("golden_visual_quality_contract")!=req.get("golden_visual_quality_contract"): raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_UPSTREAM_DRIFT")
    _reopen(repo_root,r["composed_candidate_png"],"QWEN_VISUAL_QUALITY_EVIDENCE_COMPOSED_INVALID"); ev=_json(_reopen(repo_root,eb,"QWEN_VISUAL_QUALITY_EVIDENCE_EXTERNAL_INVALID"),"QWEN_VISUAL_QUALITY_EVIDENCE_EXTERNAL_INVALID"); s,b,w,a=_review(ev,req)
    if (r.get("scores"),r.get("blockers"),r.get("weighted_score"),r.get("active_blockers"))!=(s,b,w,a): raise ValueError("QWEN_VISUAL_QUALITY_EVIDENCE_VERDICT_DRIFT")
    return r
