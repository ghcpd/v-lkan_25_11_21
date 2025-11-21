"""
Generate summary statistics from collected metric JSONL data.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List


def _load_records(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


class MetricReporter:
    """Produces rolling summaries for the provided JSONL metrics."""

    def __init__(self, source_path: str | Path, window_seconds: int = 300) -> None:
        self.source = Path(source_path)
        self.window_seconds = window_seconds

    def _filter_window(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not records or self.window_seconds <= 0:
            return records
        cutoff = time.time() - self.window_seconds
        return [rec for rec in records if rec.get("timestamp", 0) >= cutoff]

    def _aggregate_cpu(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        per_core_samples: List[List[float]] = []
        totals: List[float] = []
        max_len = 0
        for rec in records:
            cpu_info = rec.get("cpu", {})
            total = cpu_info.get("total")
            per_core = cpu_info.get("per_core", [])
            if isinstance(total, (int, float)):
                totals.append(float(total))
            if isinstance(per_core, list):
                per_core_samples.append(per_core)
                max_len = max(max_len, len(per_core))
        per_core_avg: List[float] = []
        for idx in range(max_len):
            values = [sample[idx] for sample in per_core_samples if len(sample) > idx]
            per_core_avg.append(statistics.fmean(values) if values else 0.0)
        return {
            "average_total": statistics.fmean(totals) if totals else 0.0,
            "average_per_core": per_core_avg,
        }

    def _aggregate_memory(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        used_values: List[int] = []
        available_values: List[int] = []
        timestamps: List[int] = []
        for rec in records:
            mem = rec.get("memory", {})
            used = mem.get("used")
            available = mem.get("available")
            if isinstance(used, (int, float)):
                used_values.append(int(used))
            if isinstance(available, (int, float)):
                available_values.append(int(available))
            timestamps.append(rec.get("timestamp", 0))
        trend = 0
        if used_values:
            trend = used_values[-1] - used_values[0]
        return {
            "average_used": statistics.fmean(used_values) if used_values else 0.0,
            "average_available": statistics.fmean(available_values) if available_values else 0.0,
            "trend_used": trend,
        }

    def _aggregate_resource(self, records: List[Dict[str, Any]], key: str) -> Dict[str, Any]:
        aggregated: Dict[str, Dict[str, float]] = {}
        for rec in records:
            section = rec.get(key, {})
            if not isinstance(section, dict):
                continue
            for name, stats in section.items():
                if not isinstance(stats, dict):
                    continue
                agg_entry = aggregated.setdefault(
                    name,
                    {"samples": 0, "total": 0.0, "used": 0.0, "free": 0.0, "bytes_sent": 0.0, "bytes_recv": 0.0},
                )
                agg_entry["samples"] += 1
                if "total" in stats:
                    agg_entry["total"] += float(stats.get("total", 0.0))
                if "used" in stats:
                    agg_entry["used"] += float(stats.get("used", 0.0))
                if "free" in stats:
                    agg_entry["free"] += float(stats.get("free", 0.0))
                if "bytes_sent" in stats:
                    agg_entry["bytes_sent"] += float(stats.get("bytes_sent", 0.0))
                if "bytes_recv" in stats:
                    agg_entry["bytes_recv"] += float(stats.get("bytes_recv", 0.0))

        normalized: Dict[str, Dict[str, float]] = {}
        for name, data in aggregated.items():
            samples = data.get("samples", 1) or 1
            normalized[name] = {
                "average_total": data.get("total", 0.0) / samples,
                "average_used": data.get("used", 0.0) / samples,
                "average_free": data.get("free", 0.0) / samples,
                "average_bytes_sent": data.get("bytes_sent", 0.0) / samples,
                "average_bytes_recv": data.get("bytes_recv", 0.0) / samples,
            }
        return normalized

    def generate_summary(self) -> Dict[str, Any]:
        records = _load_records(self.source)
        windowed = self._filter_window(records)
        if not windowed:
            now = int(time.time())
            return {
                "window_start": now,
                "window_end": now,
                "records": 0,
                "cpu": {"average_total": 0.0, "average_per_core": []},
                "memory": {"average_used": 0.0, "average_available": 0.0, "trend_used": 0.0},
                "disk": {},
                "network": {},
            }
        return {
            "window_start": int(windowed[0]["timestamp"]),
            "window_end": int(windowed[-1]["timestamp"]),
            "records": len(windowed),
            "cpu": self._aggregate_cpu(windowed),
            "memory": self._aggregate_memory(windowed),
            "disk": self._aggregate_resource(windowed, "disk"),
            "network": self._aggregate_resource(windowed, "network"),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize collected metric JSONL data.")
    parser.add_argument("--source", default="output/metrics.jsonl", help="JSONL file to analyze")
    parser.add_argument("--window", type=int, default=300, help="Window size in seconds")
    parser.add_argument("--output", default=None, help="Write summary JSON to this file")
    args = parser.parse_args()

    reporter = MetricReporter(args.source, window_seconds=args.window)
    summary = reporter.generate_summary()
    output = json.dumps(summary, indent=2)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
