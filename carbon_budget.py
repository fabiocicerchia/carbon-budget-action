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


def render(est, budget, replicas, cpu, mem, hours, intensity):
    pct = est / budget * 100 if budget else 0
    bar = "█" * min(int(pct / 5), 20)
    status = "✅ within budget" if est <= budget else "❌ OVER BUDGET"
    return "\n".join(
        [
            "## 🌍 Carbon budget check",
            "",
            f"Estimated: **{est:,.0f} gCO2e** / budget {budget:,.0f} gCO2e ({pct:.0f}%) {status}",
            "",
            f"`{bar}`",
            "",
            f"Assumptions: {replicas} replica(s) × ({cpu} CPU, {mem}) × {hours}h, "
            f"grid {intensity} gCO2e/kWh, PUE {PUE}.",
        ]
    )


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

    est = estimate_gco2e(
        replicas, parse_cpu(cpu), parse_memory_gb(mem), hours, intensity
    )
    within = est <= budget
    summary = render(est, budget, replicas, cpu, mem, hours, intensity)
    print(summary)

    if path := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(path, "a") as fh:
            fh.write(summary + "\n")
    if path := os.environ.get("GITHUB_OUTPUT"):
        with open(path, "a") as fh:
            fh.write(f"estimated-gco2e={est:.0f}\n")
            fh.write(f"within-budget={'true' if within else 'false'}\n")

    return 0 if (within or mode == "report") else 1


if __name__ == "__main__":
    sys.exit(main())
