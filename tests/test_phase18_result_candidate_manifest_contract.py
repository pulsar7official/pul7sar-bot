import pytest

from tools.phase18_compose_result_candidate_board import _result_candidates


def _payload():
    return {
        "contract": "pul7sar-result-seed-sweep-v2-provenance",
        "scenes": [
            {"family": "result_statement", "file": "result_seed_1.png", "seed": 1},
            {"family": "result_statement", "file": "result_seed_2.png", "seed": 2},
            {"family": "event_editorial", "file": "event.png", "seed": 9},
        ],
    }


def test_result_board_consumes_scene_contract_not_legacy_candidates_key():
    candidates = _result_candidates(_payload())
    assert [c["seed"] for c in candidates] == [1, 2]
    assert [c["file"] for c in candidates] == ["result_seed_1.png", "result_seed_2.png"]


def test_result_board_rejects_legacy_or_unknown_contract():
    payload = _payload()
    payload["contract"] = "pul7sar-result-seed-sweep-v1"
    with pytest.raises(ValueError, match="UNTRUSTED_RESULT_SWEEP_CONTRACT"):
        _result_candidates(payload)


def test_result_board_rejects_duplicate_file_binding():
    payload = _payload()
    payload["scenes"][1]["file"] = "result_seed_1.png"
    with pytest.raises(ValueError, match="RESULT_SEED_SWEEP_FILE_BINDINGS_INVALID"):
        _result_candidates(payload)


def test_result_board_rejects_duplicate_seed_binding():
    payload = _payload()
    payload["scenes"][1]["seed"] = 1
    with pytest.raises(ValueError, match="RESULT_SEED_SWEEP_SEEDS_INVALID"):
        _result_candidates(payload)
