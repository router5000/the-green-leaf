"""Tests for the blocking fact gate (scripts/validate_facts.py). No network."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import validate_facts as vf  # noqa: E402

LEAFLY = "https://www.leafly.com/strains/kandy-kush"
DNA = "https://www.dnagenetics.eu/awards/"

BUNDLE = {
    "sources": [
        {"url": LEAFLY, "text": "Kandy Kush strain aka Candy Kush. Hybrid. THC 18%. "
                                "Kandy Kush is a cross of OG Kush and Trainwreck bred by DNA Genetics."},
        {"url": DNA, "text": "Awards: Kandy Kush 1st place Indica, 2010 Colorado Cannabis Crown. "
                             "Kandy Kush (OG Kush x Trainwreck)."},
    ]
}

GOOD = {
    "keyword": "kandy kush strain",
    "title": "Kandy Kush Strain Profile",
    "content": (
        "## What Is Kandy Kush?\n"
        f"Kandy Kush is a cross of OG Kush and Trainwreck from DNA Genetics[[1]](#user-content-fn-1).\n"
        "Leafly lists a reported 18% THC for Kandy Kush[[1]](#user-content-fn-1).\n"
        "It took 1st place for indica at the 2010 Colorado Cannabis Crown[[2]](#user-content-fn-2).\n\n"
        "## Sources\n"
        f'<a id="user-content-fn-1"></a>\n1. [Leafly: Kandy Kush]({LEAFLY}) - strain page\n'
        f'<a id="user-content-fn-2"></a>\n2. [DNA Genetics awards]({DNA}) - awards list\n'
    ),
}


def ok_urls(url):
    return 200


def all_supported(items):
    return [{"supported": True, "reason": "ok"} for _ in items]


def run(article, bundle=BUNDLE, **kw):
    kw.setdefault("url_checker", ok_urls)
    kw.setdefault("support_checker", all_supported)
    return vf.validate(article, bundle, **kw)


def rules(res):
    return {e["rule"] for e in res.errors}


def with_body(extra_line):
    a = dict(GOOD)
    a["content"] = GOOD["content"].replace("## Sources", extra_line + "\n\n## Sources")
    return a


def test_good_article_passes():
    r = run(GOOD)
    assert r.passed, r.errors
    assert r.claims_checked >= 3


def test_bare_homepage_fails():
    a = dict(GOOD)
    a["content"] = GOOD["content"].replace(LEAFLY, "https://www.leafly.com")
    r = run(a)
    assert not r.passed
    assert any("bare homepage" in e["detail"] for e in r.errors)


def test_non_200_url_fails():
    r = run(GOOD, url_checker=lambda u: 404 if "dnagenetics" in u else 200)
    assert "citations" in rules(r)


def test_url_outside_research_set_fails():
    a = dict(GOOD)
    a["content"] = GOOD["content"].replace(DNA, "https://example.com/some/page")
    r = run(a)
    assert any("not in research set" in e["detail"] for e in r.errors)


def test_thc_must_be_reported_and_cited():
    r = run(with_body("Kandy Kush tests at 18% THC."))
    msgs = [e["detail"] for e in r.errors if e["rule"] == "thc"]
    assert any("reported" in m for m in msgs)
    assert any("without a citation" in m for m in msgs)


def test_unsourced_thc_number_fails():
    r = run(with_body("Leafly lists a reported 25% THC for Kandy Kush[[1]](#user-content-fn-1)."))
    assert "unsupported" in rules(r)


def test_thc_in_faq_must_be_sourced():
    a = dict(GOOD, faqs=[{"question": "How strong?", "answer": "It is reported at 27% THC."}])
    r = run(a)
    assert "unsupported" in rules(r)


@pytest.mark.parametrize("line", [
    "Kandy Kush treats chronic pain.",
    "Many patients use it for pain relief.",
    "It is great for anxiety and insomnia.",
    "Its anti-inflammatory effects are well known.",
])
def test_medical_claims_fail(line):
    r = run(with_body(line))
    assert "medical" in rules(r)


def test_medical_disclaimer_allowed():
    r = run(with_body("This article is not medical advice."))
    assert r.passed, r.errors


def test_award_without_link_fails():
    r = run(with_body("It won the 2010 Colorado Cannabis Crown."))
    assert "awards" in rules(r)


def test_fabricated_award_fails():
    r = run(with_body("It won the 2012 High Times Cannabis Cup[[2]](#user-content-fn-2)."))
    assert "unsupported" in rules(r)


def test_model_rejection_fails():
    r = run(GOOD, support_checker=lambda items: [{"supported": False, "reason": "mismatch"} for _ in items])
    assert "unsupported" in rules(r)


def test_model_unavailable_fails_closed():
    def boom(items):
        raise RuntimeError("no key")
    r = run(GOOD, support_checker=boom)
    assert "model_check" in rules(r)


def test_model_unavailable_can_fail_open_when_explicit():
    def boom(items):
        raise RuntimeError("no key")
    r = run(GOOD, support_checker=boom, require_model=False)
    assert r.passed and r.warnings


def test_missing_sources_section_fails():
    a = dict(GOOD, content="Kandy Kush is a hybrid.")
    assert "citations" in rules(run(a))


def test_dangling_citation_number_fails():
    r = run(with_body("Kandy Kush is popular[[7]](#user-content-fn-7)."))
    assert any("[7]" in e["detail"] for e in r.errors)


LAW_SRC = "https://cannabis.ny.gov/adult-use"


def law_article(last_checked=True, gov=True):
    url = LAW_SRC if gov else "https://norml.org/laws/new-york-penalties/"
    body = ("## Is Weed Legal in New York?\n"
            "Adults 21 and older may possess up to 3 ounces of cannabis[[1]](#user-content-fn-1).\n"
            + ("Last checked: 2026-10-20\n" if last_checked else "") +
            f'\n## Sources\n<a id="user-content-fn-1"></a>\n1. [NY OCM]({url}) - adult-use rules\n')
    bundle = {"sources": [{"url": url, "text": "Adults 21 and older can possess up to 3 ounces of cannabis."}]}
    return {"keyword": "is weed legal in new york", "title": "NY cannabis laws", "content": body}, bundle


def test_law_page_passes_with_gov_and_date():
    a, b = law_article()
    r = run(a, b)
    assert r.passed, r.errors


def test_law_page_needs_gov_source():
    a, b = law_article(gov=False)
    assert any(".gov" in e["detail"] for e in run(a, b).errors)


def test_law_page_needs_last_checked():
    a, b = law_article(last_checked=False)
    assert any("Last checked" in e["detail"] for e in run(a, b).errors)


def test_support_model_is_not_generator_model():
    assert vf.SUPPORT_MODEL != vf.GENERATOR_MODEL


def test_is_bare_homepage():
    assert vf.is_bare_homepage("https://www.leafly.com")
    assert vf.is_bare_homepage("https://norml.org/")
    assert not vf.is_bare_homepage("https://norml.org/laws/")
