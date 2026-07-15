from carbon_budget import (
    estimate_gco2e,
    parse_cpu,
    parse_manifest,
    parse_memory_gb,
    render,
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


def test_estimate_scales_linearly_with_replicas():
    one = estimate_gco2e(1, 1.0, 1.0, 720, 480)
    three = estimate_gco2e(3, 1.0, 1.0, 720, 480)
    assert abs(three - one * 3) < 1e-6
    # 1 core + 1 GB ≈ 4.4W → 3.8 kWh/mo * 1.2 PUE * 480 g ≈ 1.8 kg
    assert 1500 < one < 2200


def test_render_over_budget_flags():
    out = render(1200, 1000, 2, "1", "1Gi", 720, 480)
    assert "OVER BUDGET" in out and "120%" in out
