"""Source-text extraction, boilerplate detection, % parsing and model-JSON
robustness. Uses saved HTML fixtures (fetched with curl 2026-10-26); no network."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import research  # noqa: E402
import enrich_strains as es  # noqa: E402

FX = Path(__file__).parent / "fixtures"


def fixture(name):
    return (FX / name).read_text(encoding="utf-8")


# ── real-page extraction ─────────────────────────────────────────────────────

@pytest.mark.parametrize("fname,subject,must", [
    ("leafly_jillybean.html", "Jillybean",
     ["bred by crossing Orange Velvet and Space Queen", "tangy oranges and mango"]),
    ("leafly_kandy-kush.html", "Kandy Kush",
     ["DNA Genetics", "OG Kush", "Trainwreck", "lemon-Kush scent"]),
    ("thekindgoods_wedding-crasher.html", "Wedding Crasher",
     ["Wedding Cake", "Purple Punch", "Symbiotic Genetics"]),
])
def test_real_pages_yield_strain_text(fname, subject, must):
    title, text = research.html_to_text(fixture(fname))
    for m in must:
        assert m in text, m
    assert research.boilerplate_reason(text, subject) == ""
    assert "accept all cookies" not in text.lower()


def test_leafly_facts_extracted_from_next_data():
    _, text = research.html_to_text(fixture("leafly_kandy-kush.html"))
    src = research.Source(url="https://www.leafly.com/strains/kandy-kush", domain="leafly.com",
                          kind="strain_db", text=text, status=200)
    facts = research.extract_facts(src, "Kandy Kush")
    fields = {(f.field, f.value) for f in facts}
    assert ("lineage", "og kush x trainwreck") in fields
    assert any(f.field == "thc_pct" for f in facts)


def test_old_extractor_would_have_kept_boilerplate_but_new_detector_drops_it():
    page = """<html><head><title>Jillybean | Leafly</title></head><body>
    <div id="onetrust-banner"><p>We use cookies to improve your experience. Accept all cookies.</p></div>
    <nav><a>Strains</a><a>Dispensaries</a><a>Deals</a><a>Log in</a></nav>
    <p>Jillybean</p><footer>Privacy policy · Terms of use</footer></body></html>"""
    _, text = research.html_to_text(page)
    assert research.boilerplate_reason(text, "Jillybean") != ""
    assert research.boilerplate_reason("Accept cookies. Privacy policy. Menu. Log in.", "") != ""


def test_mentions_subject_plural_tolerant():
    assert research.mentions_subject("Wedding Crasher is a hybrid", "Wedding Crashers")
    assert research.mentions_subject("kandy-kush", "Kandy Kush")
    assert not research.mentions_subject("Wedding Cake", "Wedding Crashers")


def test_research_drops_boilerplate_and_falls_back_to_search():
    good = fixture("leafly_jillybean.html")
    pages = {
        "https://www.leafly.com/strains/jillybean": "<title>Jillybean | Leafly</title><p>Accept cookies</p>",
        "https://example-seeds.com/jillybean": (
            "<title>Jillybean seeds</title><article><p>" + "Jillybean is a hybrid strain bred by crossing "
            "Orange Velvet and Space Queen, with a reported THC of 17% in lab tests of Jillybean. " * 6
            + "</p></article>"),
        "https://other.org/jillybean": good,
    }

    def fetcher(url):
        return (200, pages[url]) if url in pages else (404, "")

    queries = []

    def search(q):
        queries.append(q)
        return ["https://example-seeds.com/jillybean", "https://other.org/jillybean"] if "THC" in q or \
            q == '"Jillybean" strain' else []

    b = research.research("Jillybean", kind="strain", fetcher=fetcher, search=search, polite_delay=0,
                          use_llm=False)
    urls = [s["url"] for s in b.sources]
    assert "https://www.leafly.com/strains/jillybean" not in urls     # boilerplate dropped
    assert "https://example-seeds.com/jillybean" in urls              # fallback used
    assert any(q == '"Jillybean" strain' for q in queries)
    lineage = [f for f in b.facts if f["field"] == "lineage"]
    assert lineage and len(lineage[0]["domains"]) >= 2               # 2-source rule still applies


# ── percentage parsing ───────────────────────────────────────────────────────

@pytest.mark.parametrize("raw,expected", [
    ("25%", [25.0]), ("18-22%", [18.0, 22.0]), ("18 – 22 %", [18.0, 22.0]), ("~20", [20.0]),
    ("20.5 percent", [20.5]), ("18-21", [18.0, 21.0]), ("17", [17.0]),
])
def test_parse_pct(raw, expected):
    assert research.parse_pct(raw) == expected


def test_parse_pct_rejects_garbage():
    with pytest.raises(ValueError):
        research.parse_pct("high")
    with pytest.raises(ValueError):
        research.parse_pct("250")


def test_corroborate_handles_percent_values():
    F = research.Fact
    facts = [F("thc_pct", "25%", "q", "https://a.com/x", "a.com"),
             F("thc_pct", "24-26", "q", "https://b.com/x", "b.com")]
    good, _, _ = research.corroborate(facts)
    assert any(f["field"] == "thc_pct" for f in good)


def test_llm_thc_values_normalized():
    text = "Dutch Treat reported THC 25% in tests."

    class C:
        class messages:
            @staticmethod
            def create(**kw):
                return SimpleNamespace(content=[SimpleNamespace(text=json.dumps(
                    [{"field": "thc_pct", "value": "25%", "quote": "reported THC 25%"}]))])
    src = research.Source(url="https://a.com", domain="a.com", kind="strain_db", text=text, status=200)
    facts = research.llm_extract_facts(src, "Dutch Treat", client=C())
    assert [f.value for f in facts] == ["25"]


# ── model JSON robustness ────────────────────────────────────────────────────

def test_parse_model_json_fenced_and_prose():
    assert research.parse_model_json('Sure!\n```json\n{"a": 1}\n```\nthanks') == {"a": 1}
    assert research.parse_model_json('Here: {"a": {"b": "}"}} trailing {junk') == {"a": {"b": "}"}}
    assert research.parse_model_json('x [1, 2] y', expect=list) == [1, 2]


def test_parse_model_json_invalid_raises():
    with pytest.raises(research.ModelJSONError):
        research.parse_model_json('{"a": 1 "b": 2}')


class FakeClient:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), []
        self.messages = self

    def create(self, **kw):
        self.calls.append(kw)
        return SimpleNamespace(content=[SimpleNamespace(text=self.replies.pop(0))])


def test_ask_model_json_retries_once():
    c = FakeClient(['{"a": 1 "b": 2}', '{"a": 1, "b": 2}'])
    assert research.ask_model_json(c, "m", "p") == {"a": 1, "b": 2}
    assert len(c.calls) == 2 and "not valid JSON" in c.calls[1]["messages"][-1]["content"]


def test_ask_model_json_gives_up_after_retry():
    c = FakeClient(['{"a": 1 "b": 2}', 'still {"bad" 1}'])
    with pytest.raises(research.ModelJSONError):
        research.ask_model_json(c, "m", "p")
    assert len(c.calls) == 2


def test_draft_fields_bad_json_fails_strain_cleanly(monkeypatch, tmp_path):
    """A bad model reply for one strain blocks that strain; others continue."""
    monkeypatch.setattr(es, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(es, "OUT_DIR", tmp_path / "out")
    monkeypatch.setattr(es, "REPORT_DIR", tmp_path / "rep")
    monkeypatch.setattr(es, "ROOT", tmp_path)
    monkeypatch.setattr(es, "sb_get_strain", lambda slug: None)
    bundle = research.ResearchBundle(subject="J1", slug="j1", kind="strain", generated_at="x",
                                     sources=[{"url": "https://a.com", "fetched_at": "x", "kind": "s", "text": "t"},
                                              {"url": "https://b.com", "fetched_at": "x", "kind": "s", "text": "t"}])
    monkeypatch.setattr(es, "research", lambda name, kind: bundle)

    def bad_draft(*a, **k):
        raise research.ModelJSONError("model returned invalid JSON: Expecting ',' delimiter")
    monkeypatch.setattr(es, "draft_fields", bad_draft)
    assert es.main(["--slug", "j1", "--slug", "j2"]) == 0
    state = json.loads((tmp_path / "state.json").read_text())
    assert state["j1"]["status"] == "blocked" and state["j2"]["status"] == "blocked"
