"""
Generate summary reports from collected metrics JSONL files.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from typing import Any, Dict, Iterable, List, Optional


def _iter_records(files: Iterable[str]) -> Iterable[Dict[str, Any]]:
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def _filter_records(records: Iterable[Dict[str, Any]], window_seconds: Optional[int], now: Optional[int] = None) -> List[Dict[str, Any]]:
    if window_seconds is None:
        return list(records)
    if now is None:
        now = int(time.time())
    cutoff = now - window_seconds
    return [r for r in records if r.get("timestamp", 0) >= cutoff]


def generate_summary(input_dir: str, prefix: str = "metrics", window_minutes: Optional[int] = None, now: Optional[int] = None) -> Dict[str, Any]:
    # Collect files matching prefix*.jsonl
    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.startswith(prefix) and f.endswith(".jsonl")]
    files.sort()
    window_seconds = window_minutes * 60 if window_minutes is not None else None
    records = _filter_records(_iter_records(files), window_seconds, now)

    if not records:
        return {
            "generated_at": int(time.time()) if now is None else now,
            "window_minutes": window_minutes,
            "samples": 0,
            "cpu": {},
            "memory": {},
            "disk": {},
            "network": {},
        }

    # CPU
    cpu_totals = [r.get("cpu", {}).get("total") for r in records if r.get("cpu", {}).get("total") is not None]
    cpu_per_core_series: List[List[float]] = []
    for r in records:
        per_core = r.get("cpu", {}).get("per_core")
        if per_core is None:
            continue
        if not cpu_per_core_series:
            cpu_per_core_series = [[] for _ in per_core]
        for idx, val in enumerate(per_core):
            if idx < len(cpu_per_core_series):
                cpu_per_core_series[idx].append(val)

    def _avg(vals: List[float]) -> Optional[float]:
        vals = [v for v in vals if v is not None]
        return sum(vals) / len(vals) if vals else None

    cpu_summary = {
        "avg_total": _avg(cpu_totals),
        "per_core_avg": [_avg(series) for series in cpu_per_core_series] if cpu_per_core_series else [],
    }

    # Memory percent
    mem_percents = [r.get("memory", {}).get("percent") for r in records if r.get("memory", {}).get("percent") is not None]
    memory_summary = {
        "percent": {
            "avg": _avg(mem_percents),
            "min": min(mem_percents) if mem_percents else None,
            "max": max(mem_percents) if mem_percents else None,
        },
        "last": records[-1].get("memory", {}),
    }

    # Disk percent per device
    disk_summary: Dict[str, Any] = {}
    for r in records:
        disk = r.get("disk", {})
        for dev, stats in disk.items():
            if dev not in disk_summary:
                disk_summary[dev] = {"percents": [], "last": stats}
            disk_summary[dev]["percents"].append(stats.get("percent"))
            disk_summary[dev]["last"] = stats
    for dev, d in disk_summary.items():
        percents = [p for p in d["percents"] if p is not None]
        disk_summary[dev] = {
            "percent_avg": _avg(percents),
            "percent_min": min(percents) if percents else None,
            "percent_max": max(percents) if percents else None,
            "last": d["last"],
        }

    # Network deltas per interface (based on cumulative counters)
    network_summary: Dict[str, Any] = {}
    # Build per-interface timeline
    iface_times: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        ts = r.get("timestamp")
        for iface, stats in r.get("network", {}).items():
            iface_times.setdefault(iface, []).append({"timestamp": ts, **stats})
    for iface, samples in iface_times.items():
        samples_sorted = sorted(samples, key=lambda s: s["timestamp"])
        first, last = samples_sorted[0], samples_sorted[-1]
        elapsed = max(1, last["timestamp"] - first["timestamp"] or 1)
        network_summary[iface] = {
            "bytes_sent_delta": last.get("bytes_sent", 0) - first.get("bytes_sent", 0),
            "bytes_recv_delta": last.get("bytes_recv", 0) - first.get("bytes_recv", 0),
            "bytes_sent_per_sec": (last.get("bytes_sent", 0) - first.get("bytes_sent", 0)) / elapsed,
            "bytes_recv_per_sec": (last.get("bytes_recv", 0) - first.get("bytes_recv", 0)) / elapsed,
        }

    return {
        "generated_at": int(time.time()) if now is None else now,
        "window_minutes": window_minutes,
        "samples": len(records),
        "cpu": cpu_summary,
        "memory": memory_summary,
        "disk": disk_summary,
        "network": network_summary,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate summary report from metrics JSONL")
    parser.add_argument("--input-dir", default="data", help="Directory containing metrics JSONL files")
    parser.add_argument("--prefix", default="metrics", help="Filename prefix for metrics files")
    parser.add_argument("--window-minutes", type=int, default=None, help="Time window in minutes for aggregation")
    parser.add_argument("--output", type=str, default=None, help="Path to write summary JSON (stdout if omitted)")
    args = parser.parse_args()

    summary = generate_summary(args.input_dir, args.prefix, args.window_minutes)
    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
    else:
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
