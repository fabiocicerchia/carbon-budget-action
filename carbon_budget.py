#!/usr/bin/env python3
"""carbon-budget — estimate a deployment's carbon footprint and gate CI on it.

Model (deliberately simple, fully documented):
  watts = replicas * (cpu_cores * W_PER_CORE + memory_gb * W_PER_GB)
  kwh   = watts / 1000 * hours * PUE
  gCO2e = kwh * grid_intensity

Constants follow the Cloud Carbon Footprint methodology (avg server CPU
~4 W/core busy-weighted, memory ~0.4 W/GB, PUE 1.2 for hyperscalers).
"""

import os
import re
import sys
from datetime import datetime, timedelta, timezone

W_PER_CORE = 4.0
W_PER_GB = 0.4
PUE = 1.2


def parse_manifest(text):
    """Pull replicas/cpu/memory requests out of a k8s Deployment/StatefulSet
    manifest.

    # ponytail: line matching, not a YAML parser — first container's first
    # `requests:` block only, single-document files only. Swap for PyYAML if
    # multi-container manifests ever need per-container budgets (that would
    # also break the "no runtime dependencies" guardrail, so do it deliberately).
    """
    out = {}
    m = re.search(r"^\s*replicas:\s*(\d+)", text, re.MULTILINE)
    if m:
        out["replicas"] = int(m.group(1))
    in_requests = False
    for line in text.splitlines():
        if re.match(r"\s*requests:\s*$", line):
            in_requests = True
            continue
        if not in_requests:
            continue
        if m := re.match(r"\s*cpu:\s*[\"']?([^\"'\s]+)", line):
            out.setdefault("cpu", m.group(1))
        elif m := re.match(r"\s*memory:\s*[\"']?([^\"'\s]+)", line):
            out.setdefault("memory", m.group(1))
        elif not re.match(r"\s+\S", line):
            in_requests = False
    return out


def fetch_live_intensity(zone, token, timeout=15):
    """Query Electricity Maps for the current carbon intensity of a zone.

    Returns None on any failure (network, auth, unknown zone) so the caller
    falls back to the static grid-intensity input instead of failing the gate
    on an API hiccup. Uses stdlib urllib, not `requests` — see CLAUDE.md's
    no-runtime-dependencies guardrail.
    """
    import json
    import urllib.parse
    import urllib.request

    url = "https://api.electricitymap.org/v3/carbon-intensity/latest?" + urllib.parse.urlencode(
        {"zone": zone}
    )
    req = urllib.request.Request(url, headers={"auth-token": token})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read()).get("carbonIntensity")
    except Exception:
        return None


def find_pr_number():
    """Read the PR number out of the pull_request event payload GitHub points
    $GITHUB_EVENT_PATH at."""
    import json

    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not os.path.exists(event_path):
        return None
    with open(event_path) as fh:
        event = json.load(fh)
    return event.get("pull_request", {}).get("number") or event.get("number")


def upsert_pr_comment(repo, pr_number, token, body, timeout=15):
    """Create or update this action's PR comment (found via an HTML marker,
    so re-runs edit one comment instead of piling up new ones)."""
    import json
    import urllib.request

    marker = "<!-- carbon-budget-action -->"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    list_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    req = urllib.request.Request(list_url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        comments = json.loads(r.read())
    existing = next((c for c in comments if marker in c.get("body", "")), None)

    url = f"https://api.github.com/repos/{repo}/issues/comments/{existing['id']}" if existing else list_url
    method = "PATCH" if existing else "POST"
    payload = json.dumps({"body": f"{marker}\n{body}"}).encode()
    req = urllib.request.Request(
        url, data=payload, headers={**headers, "Content-Type": "application/json"}, method=method
    )
    urllib.request.urlopen(req, timeout=timeout)


def parse_cpu(value):
    value = str(value).strip()
    return float(value[:-1]) / 1000 if value.endswith("m") else float(value)


def parse_memory_gb(value):
    value = str(value).strip()
    units = {"Gi": 2**30, "Mi": 2**20, "Ki": 2**10, "G": 1e9, "M": 1e6}
    for suffix, mult in units.items():
        if value.endswith(suffix):
            return float(value[: -len(suffix)]) * mult / 1e9
    return float(value) / 1e9


def estimate_gco2e(replicas, cpu_cores, memory_gb, hours, grid_intensity):
    watts = replicas * (cpu_cores * W_PER_CORE + memory_gb * W_PER_GB)
    kwh = watts / 1000 * hours * PUE
    return kwh * grid_intensity


def amortized_embodied_gco2e(embodied_gco2e_per_replica, lifetime_years, hours, replicas):
    """Allocate a share of each replica's underlying server's manufacturing
    (embodied) carbon to this run, proportional to hours run over the
    server's expected lifetime."""
    if not embodied_gco2e_per_replica or not lifetime_years:
        return 0.0
    lifetime_hours = lifetime_years * 365 * 24
    return embodied_gco2e_per_replica * (hours / lifetime_hours) * replicas


def rollover_burn(burned_gco2e, window_start, hours, now=None):
    """Error-budget style window rollover: carry `burned_gco2e` forward while
    the window (started at `window_start`, `hours` long) is still open, reset
    to 0 once it's elapsed. `window_start` is caller-supplied and persisted
    across runs the same way `base-gco2e` already is — this action has no
    storage of its own, see CLAUDE.md's no-runtime-dependencies guardrail.
    """
    now = now or datetime.now(timezone.utc)
    if window_start:
        started = datetime.fromisoformat(window_start.replace("Z", "+00:00"))
        if now - started < timedelta(hours=hours):
            return burned_gco2e, started
    return 0.0, now


def render(est, budget, replicas, cpu, mem, hours, intensity, base=None, embodied=0.0, burn=None):
    pct = est / budget * 100 if budget else 0
    bar = "█" * min(int(pct / 5), 20)
    status = "✅ within budget" if est <= budget else "❌ OVER BUDGET"
    lines = [
        "## 🌍 Carbon budget check",
        "",
        f"Estimated: **{est:,.0f} gCO2e** / budget {budget:,.0f} gCO2e ({pct:.0f}%) {status}",
        "",
        f"`{bar}`",
        "",
        f"Assumptions: {replicas} replica(s) × ({cpu} CPU, {mem}) × {hours}h, "
        f"grid {intensity} gCO2e/kWh, PUE {PUE}.",
    ]
    if embodied:
        lines.append(f"Includes {embodied:,.0f} gCO2e amortized embodied carbon.")
    if base is not None:
        delta = est - base
        arrow = "▲" if delta > 0 else "▼" if delta < 0 else "▬"
        pct_delta = delta / base * 100 if base else 0
        lines += ["", f"Δ vs base: {arrow} {delta:+,.0f} gCO2e ({pct_delta:+.0f}%)"]
    if burn is not None:
        total, window_start = burn
        pct_b = total / budget * 100 if budget else 0
        b_status = "✅ within budget" if total <= budget else "❌ BUDGET EXHAUSTED"
        lines += [
            "",
            f"Window burn: **{total:,.0f} gCO2e** / budget {budget:,.0f} gCO2e "
            f"({pct_b:.0f}%) {b_status} — window started {window_start.isoformat()}",
        ]
    return "\n".join(lines)


def main():
    budget = float(os.environ["BUDGET_GCO2E"])
    intensity = float(os.environ.get("GRID_INTENSITY", "480"))
    replicas = int(os.environ.get("REPLICAS", "1"))
    cpu = os.environ.get("CPU_REQUEST", "500m")
    mem = os.environ.get("MEMORY_REQUEST", "512Mi")
    hours = float(os.environ.get("HOURS", "720"))
    mode = os.environ.get("MODE", "gate")

    if manifest_path := os.environ.get("MANIFEST_PATH"):
        with open(manifest_path) as fh:
            parsed = parse_manifest(fh.read())
        replicas = parsed.get("replicas", replicas)
        cpu = parsed.get("cpu", cpu)
        mem = parsed.get("memory", mem)

    if (em_zone := os.environ.get("EM_ZONE")) and (em_token := os.environ.get("EM_TOKEN")):
        if (live := fetch_live_intensity(em_zone, em_token)) is not None:
            intensity = live

    embodied = amortized_embodied_gco2e(
        float(os.environ.get("EMBODIED_GCO2E", "0")),
        float(os.environ.get("EMBODIED_LIFETIME_YEARS", "4")),
        hours,
        replicas,
    )
    est = (
        estimate_gco2e(replicas, parse_cpu(cpu), parse_memory_gb(mem), hours, intensity)
        + embodied
    )
    base = float(base_env) if (base_env := os.environ.get("BASE_GCO2E")) else None

    # Error-budget mode: caller passes back what a previous run output for
    # BURNED_GCO2E/WINDOW_START (same pattern as BASE_GCO2E) so the budget
    # applies to the window's running total, not just this one estimate —
    # already-running workloads keep running either way, so this decides
    # whether *this* deploy should proceed, not whether to tear anything down.
    burn = None
    tracking = os.environ.get("TRACK_BUDGET", "").lower() == "true"
    if tracking:
        carried, window_start = rollover_burn(
            float(os.environ.get("BURNED_GCO2E", "0")), os.environ.get("WINDOW_START", ""), hours
        )
        total = carried + est
        burn = (total, window_start)
        within = total <= budget
    else:
        within = est <= budget

    summary = render(est, budget, replicas, cpu, mem, hours, intensity, base=base, embodied=embodied, burn=burn)
    print(summary)

    if path := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(path, "a") as fh:
            fh.write(summary + "\n")
    if path := os.environ.get("GITHUB_OUTPUT"):
        with open(path, "a") as fh:
            fh.write(f"estimated-gco2e={est:.0f}\n")
            fh.write(f"within-budget={'true' if within else 'false'}\n")
            if burn is not None:
                total, window_start = burn
                # Skipped deploys shouldn't add their own footprint to the
                # running total, only a deploy that actually goes ahead does.
                carried_forward = total if within else total - est
                fh.write(f"burned-gco2e={carried_forward:.0f}\n")
                fh.write(f"window-start={window_start.isoformat()}\n")

    if os.environ.get("PR_COMMENT", "").lower() == "true":
        token = os.environ.get("GITHUB_TOKEN")
        repo = os.environ.get("GITHUB_REPOSITORY")
        pr_number = find_pr_number()
        if token and repo and pr_number:
            try:
                upsert_pr_comment(repo, pr_number, token, summary)
            except Exception as exc:
                print(f"::warning::carbon-budget-action: failed to post PR comment: {exc}")

    return 0 if (within or mode == "report") else 1


if __name__ == "__main__":
    sys.exit(main())
