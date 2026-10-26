"""Revision / pruning logic for scripts/enrich_strains.py. No network, no models."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import enrich_strains as es  # noqa: E402

FIX = ROOT / "tests" / "fixtures" / "revision"
LONG = " ".join(["Users report a calm, upbeat mood."] * 60)   # ~360 words of harmless filler


def load(n):
    return json.loads((FIX / n).read_text())


def test_failing_sentences_maps_cited_claims_back_and_skips_non_sentence_rules():
    f = es.failing_sentences(load("j1_errors.json"))
    assert set(f) == {"J1 is a sativa-dominant hybrid with an energetic reputation.", "J1 takes 9 weeks to flower."}


def test_prune_removes_flagged_medical_and_uncited_thc_only():
    d, removed = es.prune_flagged(load("j1_draft.json"), load("j1_errors.json"))
    text = d["short_description"] + " " + d["description"]
    assert "sativa-dominant" not in text
    assert "9 weeks" not in text
    assert "patients" not in text                    # medical regex, even though not in errors
    assert "18% THC" not in text                     # THC % with no claim/citation
    assert "Leafly describes J1 as a hybrid strain." in text
    assert "skunky and sweet" in text
    assert {c["sentence"] for c in d["claims"]} == {"Leafly describes J1 as a hybrid strain."}
    assert len(removed) == 4


def test_cited_thc_is_kept():
    d = {"short_description": "", "description": "Leafly lists a reported 18% THC.",
         "claims": [{"sentence": "Leafly lists a reported 18% THC.", "url": "https://www.leafly.com/strains/j1"}]}
    out, removed = es.prune_flagged(d, [])
    assert out["description"] == "Leafly lists a reported 18% THC." and not removed


def test_disclaimer_not_pruned_as_medical():
    d = {"description": "This page is not medical advice.", "claims": []}
    out, removed = es.prune_flagged(d, [])
    assert out["description"] == "This page is not medical advice." and not removed


def test_apply_revision_only_touches_failing_sentences():
    rev = {"edits": [
        {"sentence": "J1 is a sativa-dominant hybrid with an energetic reputation.", "action": "rewrite",
         "new": "Leafly lists J1 as a hybrid.", "url": "https://www.leafly.com/strains/j1"},
        {"sentence": "J1 takes 9 weeks to flower.", "action": "delete"},
        {"sentence": "The aroma is described as skunky and sweet.", "action": "delete"},   # not failing: ignored
    ]}
    d = es.apply_revision(load("j1_draft.json"), load("j1_errors.json"), rev)
    assert d["short_description"] == "Leafly lists J1 as a hybrid."
    assert "9 weeks" not in d["description"]
    assert "skunky and sweet" in d["description"]
    assert "It helps with depression" in d["description"]   # reviser didn't touch; left for prune
    assert {"sentence": "Leafly lists J1 as a hybrid.", "url": "https://www.leafly.com/strains/j1"} in d["claims"]


def _validator_flagging(*bad):
    def v(d):
        errs = []
        for s in es.split_sentences(d.get("short_description", "") + " " + d.get("description", "")):
            if any(b in s for b in bad):
                errs.append({"rule": "unsupported", "detail": "model: not supported", "claim": s})
        return errs
    return v


def test_gate_revises_then_passes():
    draft = {"short_description": "Wedding Crashers is bred by Symbiotic Genetics.", "description": LONG, "claims": []}
    calls = []

    def reviser(d, errs):
        calls.append([e["claim"] for e in errs])
        return es.apply_revision(d, errs, {"edits": [{"sentence": errs[0]["claim"], "action": "delete"}]})

    out, reasons, log = es.gate("Wedding Crashers", {"name": "Wedding Crashers"}, draft, {},
                                validator=_validator_flagging("Symbiotic"), reviser=reviser)
    assert reasons == [] and log["revisions"] == 1 and log["pruned"] == []
    assert calls == [["Wedding Crashers is bred by Symbiotic Genetics."]]
    assert "Symbiotic" not in out["short_description"]


def test_gate_two_revisions_max_then_prunes():
    draft = {"short_description": "Jillybean has an orange candy-like aroma.", "description": LONG, "claims": []}
    n = []

    def stubborn(d, errs):
        n.append(1)
        return d   # revision fails to fix anything

    out, reasons, log = es.gate("Jillybean", {"name": "Jillybean"}, draft, {},
                                validator=_validator_flagging("candy-like"), reviser=stubborn)
    assert len(n) == 2 and log["revisions"] == 2
    assert reasons == [] and out["short_description"] == ""
    assert log["pruned"][0]["sentence"] == "Jillybean has an orange candy-like aroma."


def test_gate_insufficient_material_after_prune():
    draft = {"short_description": "Dutch Treat treats insomnia.",
             "description": "Users report feeling relaxed. It treats chronic pain for patients.", "claims": []}
    out, reasons, log = es.gate("Dutch Treat", {"name": "Dutch Treat"}, draft, {},
                                validator=lambda d: [], reviser=lambda d, e: d)
    assert out["description"] == "Users report feeling relaxed."
    assert reasons and reasons[-1].startswith(es.INSUFFICIENT)


def test_gate_keeps_unprunable_errors():
    errs = [{"rule": "citations", "detail": "no numbered ## Sources section", "claim": ""}]
    draft = {"short_description": "", "description": LONG, "claims": []}
    out, reasons, log = es.gate("X", {"name": "X"}, draft, {}, validator=lambda d: errs,
                                reviser=lambda d, e: (_ for _ in ()).throw(AssertionError("no revision")))
    assert reasons == ["[citations] no numbered ## Sources section"]


def test_structured_facts_skips_conflicts():
    b = {"facts": [{"field": "type", "value": "hybrid", "evidence": [{"url": "u1"}]},
                   {"field": "thc_pct", "value": "18%", "evidence": [{"url": "u1"}, {"url": "u2"}]}],
         "conflicts": [{"field": "thc_pct", "values": [{"value": "18%", "domains": ["a"]}, {"value": "25%", "domains": ["b"]}]}]}
    sf = es.structured_facts(b)
    assert sf["type"] == {"value": "hybrid", "sources": ["u1"]}
    assert sf["thc"] == [] and sf["conflicts"][0]["field"] == "thc_pct"
