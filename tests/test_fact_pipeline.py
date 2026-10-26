"""Tests for research corroboration, strain word counts and the publish gate. No network."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import research  # noqa: E402
import enrich_strains as es  # noqa: E402


def src(url, text, kind="strain_db"):
    return research.Source(url=url, domain=research.base_domain(url), kind=kind, text=text, status=200)


def test_corroboration_requires_two_domains():
    a = src("https://www.leafly.com/strains/zoap", "Zoap is a hybrid strain. Zoap THC 21% reported.")
    b = src("https://weedmaps.com/strains/zoap", "Zoap hybrid. Zoap THC 20-22%")
    c = src("https://www.leafly.com/news/zoap", "Zoap won the 2021 Zalympix, 1st place.")
    facts = sum((research.extract_facts(s, "Zoap") for s in (a, b, c)), [])
    good, single, _ = research.corroborate(facts)
    fields = {(f["field"], f["value"]) for f in good}
    assert ("type", "hybrid") in fields
    assert any(f["field"] == "thc_pct" for f in good)          # 21 overlaps 20-22
    assert not any(f["field"] == "award" for f in good)         # only one domain
    assert any(f["field"] == "award" for f in single)


def test_conflicting_thc_recorded():
    a = src("https://www.leafly.com/strains/x-kush", "X Kush THC 18%. X Kush is a hybrid")
    b = src("https://www.allbud.com/x-kush", "X Kush THC 28%. X Kush is an indica")
    facts = sum((research.extract_facts(s, "X Kush") for s in (a, b)), [])
    _, _, conflicts = research.corroborate(facts)
    assert {c["field"] for c in conflicts} >= {"thc_pct", "type"}


def test_soft_404_and_bare_domains():
    assert research.base_domain("https://www.leafly.com/strains/a") == "leafly.com"
    assert research.base_domain("https://cannabis.ny.gov/x") == "cannabis.ny.gov"


def test_visible_word_count_mirrors_ts():
    s = {"name": "Kandy Kush", "short_description": "a b c", "description": "one two",
         "aka": ["Candy Kush"], "effects": [{"effect_name": "Relaxed"}],
         "terpenes": [{"terpene_name": "limonene"}], "genetics": [{"parent_strain_name": "OG Kush"}],
         "flavors": ["sweet"], "aromas": [], "colors": ["green"], "origin_country": "United States",
         "difficulty": "moderate", "yield_indoor": None}
    assert es.visible_word_count(s) == 2 + 3 + 2 + 2 + 1 + 1 + 2 + 1 + 1 + 2 + 1


def test_sanitize_drops_medical_effects():
    d = es.sanitize({"effects": [{"effect_name": "Pain Relief", "effect_type": "medical"},
                                 {"effect_name": "Happy", "effect_type": "positive"}]})
    assert [e["effect_name"] for e in d["effects"]] == ["Happy"]


def test_as_article_attaches_citations():
    d = {"short_description": "Zoap is a hybrid.", "description": "Leafly lists a reported 21% THC.",
         "claims": [{"sentence": "Leafly lists a reported 21% THC.", "url": "https://www.leafly.com/strains/zoap"}]}
    art = es.as_article("Zoap", d)
    assert "[[1]](#user-content-fn-1)" in art["content"]
    assert "https://www.leafly.com/strains/zoap" in art["content"]


def test_publish_gate_requires_fact_check(tmp_path):
    import importlib
    ap = importlib.import_module("auto_publish")
    ok = tmp_path / "ok.md"
    ok.write_text("---\ntitle: x\nqa_score: 6.0\nfact_check_passed: true\n---\nbody")
    bad = tmp_path / "bad.md"
    bad.write_text("---\ntitle: x\nqa_score: 9.5\nqa_passed: true\n---\nbody")
    legacy = tmp_path / "legacy.md"
    legacy.write_text("no frontmatter")
    assert ap.check_article_qa(ok)[0] is True          # low style score no longer blocks
    assert ap.check_article_qa(bad)[0] is False        # high style score alone can't publish
    assert ap.check_article_qa(legacy)[0] is False     # fail closed
