"""Type-consistency gate and THC single-value handling. No network, no models."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import enrich_strains as es  # noqa: E402
from research import parse_pct, norm_pct  # noqa: E402


def bundle(*types, conflict=False):
    b = {"facts": [{"field": "type", "value": t, "evidence": [{"url": f"https://s{i}.example"}]}
                   for i, t in enumerate(types)], "conflicts": []}
    if conflict:
        b["conflicts"] = [{"field": "type", "values": [{"value": t} for t in types]}]
    return b


def draft(text):
    return {"short_description": text, "description": ""}


def test_stated_types():
    assert es.stated_types("J1 is a sativa-dominant hybrid.") == {"hybrid"}
    assert es.stated_types("An indica-dominant strain.") == {"hybrid"}
    assert es.stated_types("A classic indica.") == {"indica"}
    assert es.stated_types("No type here.") == set()


def test_text_disagreeing_with_stored_type_is_flagged():   # J1 case
    t, r = es.check_type_consistency("sativa", draft("J1 is a balanced hybrid."), bundle())
    assert t is None and r and r[0].startswith(es.TYPE_CONFLICT)


def test_stored_vs_sourced_conflict_is_flagged_not_overwritten():   # Kandy Kush case
    t, r = es.check_type_consistency("indica", draft("Kandy Kush is a hybrid."), bundle("hybrid", "hybrid"))
    assert t is None
    assert any("sources say 'hybrid'" in x for x in r)


def test_agreement_passes():
    assert es.check_type_consistency("indica", draft("A heavy indica."), bundle("indica")) == (None, [])
    assert es.check_type_consistency("hybrid", draft("No type sentence."), bundle()) == (None, [])


def test_empty_stored_type_is_filled_from_sources():
    assert es.check_type_consistency(None, draft("A hybrid."), bundle("hybrid")) == ("hybrid", [])


def test_conflicting_sources_give_no_sourced_type():
    assert es.sourced_type(bundle("indica", "hybrid", conflict=True)) is None


def test_single_thc_value_parses_to_one_number():
    assert parse_pct("21%") == [21.0]
    assert norm_pct("21-21%") == "21"
    vals = parse_pct("21%")
    assert (min(vals), max(vals)) == (21.0, 21.0)   # stored min==max; site renders "21%"
