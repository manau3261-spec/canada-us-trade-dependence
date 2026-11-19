"""Presentation and Streamlit integration checks against the locked official data."""

import asyncio
import io
import json
from pathlib import Path
import re

import fitz
import numpy as np
import pandas as pd
import pytest
from starlette.applications import Starlette
from streamlit.runtime.memory_media_file_storage import MemoryMediaFileStorage
from streamlit.web.server.starlette.starlette_routes import create_media_routes
from streamlit.testing.v1 import AppTest

from trade_audit.acquire import sha256
from trade_audit.phase3_figures import PRODUCTS
from trade_audit.phase5_data import (
    INPUTS, bridge, destination_slice, exposure, fact_values, hhi_trend, load, localized_number, primary,
)
from trade_audit.phase5_paper import F, figure, interpolate, render, tables
from trade_audit.sources import JURISDICTIONS, PROVINCES

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT/"paper"


@pytest.fixture(scope="module")
def data():
    return load(ROOT)


def test_locked_inputs_and_frequency_units(data):
    assert set(data) == set(INPUTS)
    for key in ("annual","monthly"):
        d=data[key]
        valid=d.world_cad_thousands.gt(0) & d.us_share.notna()
        np.testing.assert_allclose(d.loc[valid,"us_share"],
                                   d.loc[valid,"us_cad_thousands"]/d.loc[valid,"world_cad_thousands"],atol=1e-12)
        np.testing.assert_allclose(d.non_us_cad_thousands, d.world_cad_thousands-d.us_cad_thousands,atol=1e-7)
        assert set(d.geo)=={"Canada",*JURISDICTIONS}
        assert set(d["product"])=={"TOTAL",*PRODUCTS}
    with pytest.raises(ValueError,match="annual"):
        exposure(data,"Annual","2025-01","2025-12",["Canada"],["TOTAL"])
    with pytest.raises(ValueError,match="monthly"):
        exposure(data,"Monthly","2025","2026",["Canada"],["TOTAL"])
    assert len(exposure(data,"Annual","2010","2025",["Canada"],["TOTAL"]))==16
    assert len(exposure(data,"Monthly","2025-01","2026-09",["Canada"],["TOTAL"]))==21


def test_concentration_gaps_and_commodity_reconciliation(data):
    d=hhi_trend(data,"Canada","2019","2025").set_index("period")
    assert np.isnan(d.loc["2020","destination_hhi_ex_us"])
    assert np.isfinite(d.loc["2020","published_destination_hhi_ex_us"])
    other=destination_slice(data,"2024","2025",["United Kingdom","China"])
    assert len(other)==4
    np.testing.assert_allclose(other.share_of_non_us.to_numpy()[other.partner.eq("United Kingdom")],
                               [0.1571897806,0.2242611782],atol=1e-8)
    b=bridge(data).set_index("component").change_cad
    assert abs(b["total"]-28_796_022_412)<.01
    assert abs(b.loc[["710812","270900","remainder"]].sum()-b["total"])<.01
    c=data["gold_hhi"].set_index(["scope","year"])
    assert c.loc[("all products",2025),"hhi_ex_us"]-c.loc[("all products",2024),"hhi_ex_us"] > .02
    assert c.loc[("excluding HS 710812",2025),"hhi_ex_us"]-c.loc[("excluding HS 710812",2024),"hhi_ex_us"] < .003


def test_correct_primary_and_secondary_scales(data):
    p=primary(data)
    assert p["beta"]==pytest.approx(.1282721235310032)
    assert p["scaled"]==pytest.approx(.01282721235310032)
    assert (p["ci_low"],p["ci_high"])==pytest.approx((-.06048669586398414,.1052539906451989))
    assert (p["webb_p"],p["n"],p["groups"])==(.7174,1454,108)
    r=data["robustness"]
    assert len(r)==26
    assert (r.ci_low.lt(0)&r.ci_high.gt(0)).all()
    assert r.loc[r.specification.eq("D_lag_weighted"),"coefficient"].item()<0
    assert set(data["influence"].geo)==set(PROVINCES)


def test_bilingual_numerical_templates_and_figure_hashes(data):
    keys=[]
    facts=fact_values(data)
    for lang in ("en","fr"):
        doc=(PAPER/f"working_paper_{lang}.md").read_text()
        keys.append(re.findall(r"\{\{([A-Z0-9_]+)\}\}",doc))
        src=interpolate(doc,facts,tables(data,lang),lang)
        for k in set(keys[-1]):
            assert localized_number(*facts[k],lang) in src
        assert not re.search(r"\{\{(?:[A-Z]|table:)",src)
        assert set(re.findall(r"\{\{fig:([a-z_]+)\}\}",src))==set(F)
        for k in F:
            path,title,caption=figure(ROOT,k,lang)
            assert path.is_file() and title and caption
    assert sorted(keys[0])==sorted(keys[1])


def test_reproduce_self_contained_html_and_pdf(tmp_path):
    output=render(ROOT,tmp_path,make_figures=False)
    delivered=json.loads((PAPER/"rendered/manifest.json").read_text())
    for lang in ("en","fr"):
        p=f"canada_us_trade_{lang}"
        assert output[f"{p}.html"]==delivered[f"{p}.html"]
        assert output[f"{p}.pdf"]==delivered[f"{p}.pdf"]
        h=(tmp_path/f"{p}.html").read_text()
        assert '<meta name="author" content="Manau Salaun">' in h
        assert '<link rel="license" href="https://creativecommons.org/licenses/by/4.0/">' in h
        assert f'<html lang="{lang}">' in h and h.count("data:image/png;base64,")==len(F)
        assert all(x in h for x in (localized_number(.7174,4,lang),localized_number(.012827,6,lang)))
        with fitz.open(tmp_path/f"{p}.pdf") as report, fitz.open(PAPER/"rendered"/f"{p}.pdf") as expected:
            assert 19<=len(report)<=30 and len(report)==len(expected)
            assert report.metadata["author"] == "Manau Salaun"
            assert [s.get_text() for s in report]==[s.get_text() for s in expected]
            assert sum(len(s.get_images()) for s in report)==len(F)
            assert any(s.get_links() for s in report)
            assert sha256(PAPER/"rendered"/f"{p}.pdf")==delivered[f"{p}.pdf"]


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("CANADA_TRADE_ROOT",str(ROOT))
    a=AppTest.from_file(str(ROOT/"dashboard/app.py"),default_timeout=20).run()
    assert not a.exception
    return a


def change_view(app,name):
    app.radio(key="section").set_value(name).run()
    assert not app.exception


@pytest.mark.parametrize("language", ["en","fr"])
def test_dashboard_sections_have_source_and_csv_controls(app, language):
    app.radio(key="language").set_value(language).run()
    assert not app.exception
    for view, charts in {"national":1,"province":2,"products":2,"concentration":2,"decomposition":4,
                          "model":3,"pilot":1,"sources":0}.items():
        change_view(app,view)
        assert len(app.get("plotly_chart"))==charts
        assert len(app.get("download_button"))>=1
        assert any("statcan" in c.value or "census.gov" in c.value for c in app.caption) or view=="sources"


def test_national_chart_dates_and_filtered_csv(app, data, monkeypatch):
    captured={}
    original=MemoryMediaFileStorage.load_and_get_id
    def observe(self, payload, media, kind, filename=None):
        file_id=original(self,payload,media,kind,filename)
        if filename and filename.endswith(".csv"):
            captured[filename]=(self,file_id)
        return file_id
    monkeypatch.setattr(MemoryMediaFileStorage,"load_and_get_id",observe)
    app.radio(key="national_frequency").set_value("Monthly").run()
    app.select_slider(key="national_period_Monthly").set_value(("2026-07","2026-09")).run()
    assert not app.exception
    name="national_monthly_2026-07_2026-09.csv"
    storage,file_id=captured[name]
    media_app=Starlette(routes=create_media_routes(storage,None))
    messages=[]
    async def receive():
        return {"type":"http.request","body":b"","more_body":False}

    async def send(message):
        messages.append(message)

    path=f"/media/{file_id}.csv"
    asyncio.run(media_app({"type":"http","asgi":{"version":"3.0","spec_version":"2.4"},
                           "http_version":"1.1","method":"GET","scheme":"http","path":path,
                           "root_path":"","query_string":b"","headers":[]},receive,send))
    headers=dict(messages[0]["headers"])
    assert messages[0]["status"]==200
    assert headers[b"content-type"].startswith(b"text/csv")
    assert headers[b"content-disposition"]==f'attachment; filename="{name}"'.encode()
    payload=b"".join(m.get("body",b"") for m in messages[1:])
    csv=pd.read_csv(io.BytesIO(payload),dtype={"period":str})
    eligible=exposure(data,"Monthly","2026-07","2026-09",["Canada"],["TOTAL"]).reset_index(drop=True)
    pd.testing.assert_frame_equal(csv,eligible,check_dtype=False)
    trace=json.loads(app.get("plotly_chart")[0].proto.spec)["data"][0]
    assert trace["x"]==eligible.period.tolist()
    np.testing.assert_allclose(trace["y"],eligible.us_share)
    assert trace["connectgaps"] is False
    assert "national_matched_months.csv" in captured
    assert any("12-10-0175-01" in c.value for c in app.caption)


def test_province_and_product_controls(app, data):
    change_view(app,"province")
    app.selectbox(key="province_year").set_value(2024).run()
    app.radio(key="province_group").set_value("provinces").run()
    app.selectbox(key="province_measure").set_value("value").run()
    assert not app.exception
    chart=json.loads(app.get("plotly_chart")[0].proto.spec)["data"][0]
    original=exposure(data,"Annual","2024","2024",PROVINCES,["TOTAL"]).sort_values("us_cad_thousands",ascending=False)
    assert chart["y"]==original.geo.tolist()
    np.testing.assert_allclose(chart["x"],original.us_cad_thousands/1e6)
    change_view(app,"products")
    app.selectbox(key="product_geo").set_value("Ontario").run()
    app.multiselect(key="product_codes").set_value(["C19"]).run()
    app.selectbox(key="product_year").set_value(2023).run()
    assert not app.exception
    chart=json.loads(app.get("plotly_chart")[0].proto.spec)["data"][0]
    value=exposure(data,"Annual","2023","2023",["Ontario"],["C19"]).us_share.item()
    assert len(chart["x"])==1 and chart["x"][0]==pytest.approx(value)


def test_hhi_chart_toggles_benchmark_and_keeps_missing(app):
    change_view(app,"concentration")
    chart=json.loads(app.get("plotly_chart")[0].proto.spec)
    assert len(chart["data"])==4
    trace=chart["data"][1]
    assert trace["y"][trace["x"].index("2020")] is None
    app.checkbox(key="hhi_benchmark").set_value(False).run()
    app.multiselect(key="dest_compare").set_value(["China"]).run()
    chart=json.loads(app.get("plotly_chart")[0].proto.spec)
    assert len(chart["data"])==2
    assert len(json.loads(app.get("plotly_chart")[1].proto.spec)["data"])==1


def test_model_chart_uses_exact_intervals(app, data):
    change_view(app,"model")
    p=primary(data)
    trace=json.loads(app.get("plotly_chart")[0].proto.spec)["data"][0]
    assert trace["x"][0]==pytest.approx(p["scaled"])
    assert trace["x"][0]-trace["error_x"]["arrayminus"][0]==pytest.approx(p["ci_low"])
    assert trace["x"][0]+trace["error_x"]["array"][0]==pytest.approx(p["ci_high"])
    app.selectbox(key="model_robust_mode").set_value("direction").run()
    chart=json.loads(app.get("plotly_chart")[1].proto.spec)
    assert len(chart["data"][0]["x"])==2


@pytest.mark.parametrize("language", ["en", "fr"])
def test_release_additional_filters_and_exports(app, data, language):
    app.radio(key="language").set_value(language).run()
    app.select_slider(key="national_period_Annual").set_value((2024, 2025)).run()
    annual = json.loads(app.get("plotly_chart")[0].proto.spec)["data"][0]
    assert annual["x"] == ["2024", "2025"]
    np.testing.assert_allclose(annual["y"], [0.7579594046579737, 0.7168837424885757])

    change_view(app, "province")
    app.multiselect(key="province_heat_geos").set_value(["Ontario", "Quebec"]).run()
    heat = json.loads(app.get("plotly_chart")[1].proto.spec)["data"][0]
    assert len(heat["y"]) == 2

    change_view(app, "products")
    app.selectbox(key="product_history_section").set_value("C12").run()
    app.select_slider(key="product_history_period").set_value((2020, 2023)).run()
    product_trace = json.loads(app.get("plotly_chart")[1].proto.spec)["data"][0]
    assert product_trace["x"] == ["2020", "2021", "2022", "2023"]

    change_view(app, "concentration")
    app.selectbox(key="hhi_geo").set_value("Ontario").run()
    app.select_slider(key="hhi_period").set_value((2024, 2025)).run()
    hhi_trace = json.loads(app.get("plotly_chart")[0].proto.spec)["data"][1]
    expected = hhi_trend(data, "Ontario", "2024", "2025").sort_values("period")
    assert hhi_trace["x"] == expected.period.tolist()
    np.testing.assert_allclose(hhi_trace["y"], expected.destination_hhi_ex_us)

    change_view(app, "decomposition")
    app.selectbox(key="decomp_destination").set_value("GB").run()
    detail = json.loads(app.get("plotly_chart")[-1].proto.spec)["data"][0]
    assert any(item.startswith("710812") for item in detail["y"])
    assert len(app.get("download_button")) >= 5

    change_view(app, "pilot")
    app.selectbox(key="pilot_destination").set_value("MX").run()
    app.radio(key="pilot_scope").set_value("core").run()
    assert not app.exception
    assert len(app.get("download_button")) >= 3
    coverage = [x.value for x in app.dataframe if "pre_positive_months" in x.value]
    assert len(coverage) == 1 and coverage[0].country.eq("MX").all()
    assert coverage[0].scope.eq("covered_core_232").all()

    change_view(app, "sources")
    assert len(app.get("download_button")) == 2



@pytest.mark.parametrize("language", ["en", "fr"])
def test_missing_release_data_has_localized_recovery(tmp_path, monkeypatch, language):
    monkeypatch.setenv("CANADA_TRADE_ROOT", str(tmp_path))
    style = tmp_path / "dashboard"
    style.mkdir()
    (style / "style.css").write_text((ROOT / "dashboard/style.css").read_text())
    candidate = AppTest.from_file(str(ROOT / "dashboard/app.py"), default_timeout=20).run()
    candidate.radio(key="language").set_value(language).run()
    assert not candidate.exception
    assert not candidate.get("plotly_chart")
    assert not candidate.get("download_button")
    expected = "verified data are unavailable" if language == "en" else "données vérifiées sont indisponibles"
    assert expected in candidate.error[0].value
