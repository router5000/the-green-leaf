"""--from-file drafts, source requirement, strain_type correction. No network."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import enrich_strains as es  # noqa: E402

L = "https://www.leafly.com/strains/x"
A = "https://www.allbud.com/marijuana-strains/hybrid/x"


def test_unsourced_fact_rejected():
    r = es.require_sources({"flavors": ["grape"], "description": "X."}, [{"field": "description", "url": L}])
    assert any("flavors" in x for x in r)


def test_all_sourced_passes():
    d = {"description": "X.", "short_description": "X.", "flavors": ["grape"],
         "genetics": [{"parent_strain_name": "A", "parent_type": "mother"}], "thc_reported": [20, 24]}
    s = [{"field": f, "url": L} for f in ("description", "flavors", "genetics", "thc")]
    assert es.require_sources(d, s) == []


def test_homepage_and_bad_parent_type_rejected():
    r = es.require_sources({"genetics": [{"parent_strain_name": "A", "parent_type": "parent"}]},
                           [{"field": "genetics", "url": "https://leafly.com/"}])
    assert any("not a page URL" in x for x in r) and any("mother|father" in x for x in r)


def test_type_correction_needs_two_domains():
    d = {"strain_type": "indica", "short_description": "X is an indica."}
    ok, r = es.type_correction("hybrid", d, [{"field": "strain_type", "url": L}])
    assert not ok and r
    ok, r = es.type_correction("hybrid", d, [{"field": "strain_type", "url": L}, {"field": "strain_type", "url": A}])
    assert ok and r == []


def test_type_correction_blocked_by_prose():
    d = {"strain_type": "indica", "short_description": "X is a sativa."}
    ok, r = es.type_correction("hybrid", d, [{"field": "strain_type", "url": L}, {"field": "strain_type", "url": A}])
    assert not ok


def test_from_file_dry_run(tmp_path, monkeypatch):
    monkeypatch.setattr(es, "REPORT_DIR", tmp_path)
    monkeypatch.setattr(es, "sb_conf", lambda: (None, None))
    f = tmp_path / "d.json"
    f.write_text(json.dumps([
        {"slug": "good", "draft": {"flavors": ["grape"]}, "sources": [{"field": "flavors", "url": L}]},
        {"slug": "bad", "draft": {"flavors": ["grape"]}, "sources": []},
    ]))
    assert es.main(["--from-file", str(f)]) == 1
    rep = json.loads(next(tmp_path.glob("strains_from_file_*.json")).read_text())
    assert [x["slug"] for x in rep["passed_dry_run"]] == ["good"]
    assert [x["slug"] for x in rep["blocked"]] == ["bad"]


def test_source_rows_mapping():
    rows = es.to_source_rows({"id": "u", "slug": "x"}, [{"field": "flavors", "url": L, "value": "grape",
                                                         "fetched_at": "2026-11-02"}])
    assert rows[0]["source_url"] == L and rows[0]["source_name"] == "Leafly" and rows[0]["slug"] == "x"
    assert rows[0]["retrieved_at"] == "2026-11-02"
