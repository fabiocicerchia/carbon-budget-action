import json
import urllib.error
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from carbon_budget import (
    CI_API_MAX_AGE_S,
    PR_COMMENT_MARKER,
    amortized_embodied_gco2e,
    estimate_gco2e,
    fetch_ci_api_intensity,
    fetch_live_intensity,
    find_pr_number,
    parse_cpu,
    parse_manifest,
    parse_memory_gb,
    render,
    rollover_burn,
    upsert_pr_comment,
)


def test_parsers():
    assert parse_cpu("500m") == 0.5
    assert parse_cpu("2") == 2.0
    assert round(parse_memory_gb("2Gi"), 2) == 2.15


def test_parse_manifest_reads_replicas_and_first_container_requests():
    manifest = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 4
  template:
    spec:
      containers:
        - name: web
          resources:
            requests:
              cpu: 250m
              memory: 512Mi
            limits:
              cpu: 500m
"""
    assert parse_manifest(manifest) == {
        "replicas": 4,
        "cpu": "250m",
        "memory": "512Mi",
    }


def test_parse_manifest_missing_fields_return_empty_dict():
    assert parse_manifest("kind: ConfigMap\n") == {}


def test_fetch_live_intensity_returns_value_on_success():
    resp = MagicMock()
    resp.read.return_value = json.dumps({"carbonIntensity": 42}).encode()
    resp.__enter__.return_value = resp
    with patch("urllib.request.urlopen", return_value=resp):
        assert fetch_live_intensity("FR", "tok") == 42


def test_fetch_live_intensity_falls_back_to_none_on_error():
    with patch("urllib.request.urlopen", side_effect=OSError("boom")):
        assert fetch_live_intensity("FR", "tok") is None


# --- ci-api -----------------------------------------------------------------

CI_NOW = datetime(2026, 8, 8, 18, 10, tzinfo=timezone.utc)

CI_COUNTRY = {
    "country_code": "IT",
    "basis": "measured",
    "generated_at": "2026-08-08T18:00:00Z",
    "direct": 274,
    "lifecycle": 319,
    "consumption_direct": 339,
    "consumption_lifecycle": 384,
}

# Zones carry neither consumption figure: the import adjustment is a national
# number that does not describe one bidding zone.
CI_ZONE = {
    "country_code": "IT",
    "zone": "SICI",
    "basis": "measured",
    "generated_at": "2026-08-08T18:00:00Z",
    "direct": 411,
    "lifecycle": 456,
}


def _ci_urlopen(by_path):
    """Patch urlopen with a path -> payload (or exception) table, recording the
    order paths were asked for."""
    seen = []

    def open_(url, timeout=None):
        path = url.split("fabiocicerchia.it", 1)[1]
        seen.append(path)
        outcome = by_path[path]
        if isinstance(outcome, Exception):
            raise outcome
        resp = MagicMock()
        resp.read.return_value = json.dumps(outcome).encode()
        resp.__enter__.return_value = resp
        return resp

    return open_, seen


def test_ci_api_reports_consumption_lifecycle():
    open_, seen = _ci_urlopen({"/v1/last-hour/IT": CI_COUNTRY})
    with patch("urllib.request.urlopen", open_):
        # Not 274 (direct) and not 319 (lifecycle): the figure reported carries
        # both the upstream scope and the trade adjustment.
        assert fetch_ci_api_intensity("it", now=CI_NOW) == (384.0, "measured")
    assert seen == ["/v1/last-hour/IT"]


def test_ci_api_zone_falls_back_to_lifecycle():
    open_, seen = _ci_urlopen({"/v1/zones/IT/SICI": CI_ZONE})
    with patch("urllib.request.urlopen", open_):
        assert fetch_ci_api_intensity("IT/sici", now=CI_NOW) == (456.0, "measured")
    assert seen == ["/v1/zones/IT/SICI"]


def test_ci_api_zone_404_asks_the_country_after_waiting_out_the_rate_limit():
    """A zone drops out for any hour its provider had a bad minute, so a 404 is
    "ask the country instead". The retry is a second request inside the API's
    1-per-10s window, so it has to wait or it collects a 429."""
    open_, seen = _ci_urlopen(
        {
            "/v1/zones/IT/SICI": urllib.error.HTTPError(
                "u", 404, "Not Found", {}, None
            ),
            "/v1/last-hour/IT": CI_COUNTRY,
        }
    )
    waits = []
    with patch("urllib.request.urlopen", open_):
        got = fetch_ci_api_intensity("IT/SICI", sleep=waits.append, now=CI_NOW)

    assert got == (384.0, "measured")
    assert seen == ["/v1/zones/IT/SICI", "/v1/last-hour/IT"]
    assert waits == [10], "must wait out the rate limit before the second call"


def test_ci_api_refuses_a_stale_measurement():
    """Nothing in the response says it is stale — the objects are static and
    served with no application in the request path — so a missed hourly run
    only shows up as an old generated_at."""
    open_, _ = _ci_urlopen({"/v1/last-hour/IT": CI_COUNTRY})
    late = CI_NOW + timedelta(seconds=CI_API_MAX_AGE_S)
    with patch("urllib.request.urlopen", open_):
        assert fetch_ci_api_intensity("IT", now=late) is None


def test_ci_api_accepts_an_annual_average_and_names_it():
    """Unlike a spot reading, an annual average is a reasonable input to a
    720-hour projection — but the freshness rule must not be applied to it:
    annual readings are rewritten weekly, so an old generated_at is expected."""
    annual = {
        "country_code": "MX",
        "basis": "annual-average",
        "hour_start": None,
        "generated_at": "2026-08-02T00:00:00Z",  # six days old, by design
        "direct": 420,
        "lifecycle": 465,
        "consumption_lifecycle": 510,
    }
    open_, _ = _ci_urlopen({"/v1/last-hour/MX": annual})
    with patch("urllib.request.urlopen", open_):
        assert fetch_ci_api_intensity("MX", now=CI_NOW) == (510.0, "annual-average")


def test_ci_api_failure_falls_back_to_the_static_input():
    with patch("urllib.request.urlopen", side_effect=OSError("boom")):
        assert fetch_ci_api_intensity("IT", now=CI_NOW) is None


def test_ci_api_needs_a_country():
    with patch("urllib.request.urlopen", side_effect=AssertionError("no request")):
        assert fetch_ci_api_intensity("  ", now=CI_NOW) is None


def test_estimate_scales_linearly_with_replicas():
    one = estimate_gco2e(1, 1.0, 1.0, 720, 480)
    three = estimate_gco2e(3, 1.0, 1.0, 720, 480)
    assert abs(three - one * 3) < 1e-6
    # 1 core + 1 GB ≈ 4.4W → 3.8 kWh/mo * 1.2 PUE * 480 g ≈ 1.8 kg
    assert 1500 < one < 2200


def test_render_over_budget_flags():
    out = render(1200, 1000, 2, "1", "1Gi", 720, 480)
    assert "OVER BUDGET" in out and "120%" in out


def test_amortized_embodied_gco2e_scales_with_hours_and_replicas():
    # 40,000 gCO2e server, 4y lifetime, 1 month (720h), 2 replicas
    got = amortized_embodied_gco2e(40000, 4, 720, 2)
    lifetime_hours = 4 * 365 * 24
    assert abs(got - 40000 * (720 / lifetime_hours) * 2) < 1e-6


def test_amortized_embodied_gco2e_zero_when_not_configured():
    assert amortized_embodied_gco2e(0, 4, 720, 2) == 0.0
    assert amortized_embodied_gco2e(1000, 0, 720, 2) == 0.0


def test_render_shows_delta_against_base():
    out = render(1200, 2000, 2, "1", "1Gi", 720, 480, base=1000)
    assert "▲ +200 gCO2e (+20%)" in out


def test_render_shows_embodied_line():
    out = render(1200, 2000, 2, "1", "1Gi", 720, 480, embodied=300)
    assert "300 gCO2e amortized embodied carbon" in out


def test_find_pr_number_reads_event_payload(tmp_path, monkeypatch):
    event = tmp_path / "event.json"
    event.write_text(json.dumps({"pull_request": {"number": 42}}))
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event))
    assert find_pr_number() == 42


def test_find_pr_number_missing_path_returns_none(monkeypatch):
    monkeypatch.delenv("GITHUB_EVENT_PATH", raising=False)
    assert find_pr_number() is None


def test_rollover_burn_no_window_start_starts_fresh():
    now = datetime(2026, 7, 27, tzinfo=timezone.utc)
    assert rollover_burn(3000, "", 720, now=now) == (0.0, now)


def test_rollover_burn_carries_forward_within_window():
    now = datetime(2026, 7, 27, tzinfo=timezone.utc)
    started = now - timedelta(hours=100)
    assert rollover_burn(3000, started.isoformat(), 720, now=now) == (3000, started)


def test_rollover_burn_resets_once_window_elapsed():
    now = datetime(2026, 7, 27, tzinfo=timezone.utc)
    started = now - timedelta(hours=800)
    assert rollover_burn(3000, started.isoformat(), 720, now=now) == (0.0, now)


def test_render_shows_window_burn_status():
    started = datetime(2026, 7, 1, tzinfo=timezone.utc)
    out = render(1200, 2000, 2, "1", "1Gi", 720, 480, burn=(2500, started))
    assert "BUDGET EXHAUSTED" in out and "2,500 gCO2e" in out


def test_upsert_pr_comment_patches_existing_marker_comment():
    list_resp = MagicMock()
    list_resp.read.return_value = json.dumps(
        [{"id": 7, "body": f"{PR_COMMENT_MARKER}\nold"}]
    ).encode()
    list_resp.__enter__.return_value = list_resp
    patch_resp = MagicMock()
    patch_resp.__enter__.return_value = patch_resp

    with patch("urllib.request.urlopen", side_effect=[list_resp, patch_resp]) as m:
        upsert_pr_comment("acme/repo", 1, "tok", "new body")

    second_call_req = m.call_args_list[1].args[0]
    assert second_call_req.get_method() == "PATCH"
    assert "/issues/comments/7" in second_call_req.full_url
